from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Workbook, WorkbookPage
from apps.worksheets.models import Worksheet


@login_required
def workbook_list(request):
    workbooks = Workbook.objects.filter(teacher=request.user)
    return render(request, 'workbooks/list.html', {'workbooks': workbooks})


@login_required
def workbook_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        if title:
            wb = Workbook.objects.create(teacher=request.user, title=title, description=description)
            messages.success(request, f'"{wb.title}" defteri oluşturuldu.')
            return redirect('workbook_detail', pk=wb.pk)
    return render(request, 'workbooks/create.html')


@login_required
def workbook_detail(request, pk):
    workbook = get_object_or_404(Workbook, pk=pk, teacher=request.user)
    my_worksheets = Worksheet.objects.filter(author=request.user).exclude(
        id__in=workbook.pages.values_list('worksheet_id', flat=True)
    )
    if request.method == 'POST':
        worksheet_id = request.POST.get('worksheet_id')
        ws = get_object_or_404(Worksheet, pk=worksheet_id, author=request.user)
        last = workbook.pages.count()
        WorkbookPage.objects.get_or_create(workbook=workbook, worksheet=ws, defaults={'order': last + 1})
        messages.success(request, 'Sayfa eklendi.')
        return redirect('workbook_detail', pk=pk)
    return render(request, 'workbooks/detail.html', {
        'workbook': workbook,
        'my_worksheets': my_worksheets,
    })


@login_required
def workbook_remove_page(request, pk, page_pk):
    workbook = get_object_or_404(Workbook, pk=pk, teacher=request.user)
    page = get_object_or_404(WorkbookPage, pk=page_pk, workbook=workbook)
    page.delete()
    messages.success(request, 'Sayfa kaldırıldı.')
    return redirect('workbook_detail', pk=pk)


@login_required
def workbook_delete(request, pk):
    workbook = get_object_or_404(Workbook, pk=pk, teacher=request.user)
    if request.method == 'POST':
        title = workbook.title
        workbook.delete()
        messages.success(request, f'"{title}" defteri silindi.')
        return redirect('workbook_list')
    return render(request, 'workbooks/confirm_delete.html', {'workbook': workbook})
