from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Assignment
from apps.accounts.models import Classroom
from apps.worksheets.models import Worksheet
from apps.workbooks.models import Workbook


@login_required
def assignment_list(request):
    if request.user.is_teacher:
        assignments = Assignment.objects.filter(created_by=request.user)
    else:
        assignments = Assignment.objects.filter(
            classrooms__students=request.user
        ).distinct()
    return render(request, 'assignments/list.html', {'assignments': assignments})


@login_required
def assignment_create(request):
    if not request.user.is_teacher:
        messages.error(request, 'Sadece öğretmenler ödev oluşturabilir.')
        return redirect('dashboard')
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        worksheet_id = request.POST.get('worksheet_id')
        workbook_id = request.POST.get('workbook_id')
        due_date = request.POST.get('due_date') or None
        classroom_ids = request.POST.getlist('classroom_ids')
        allow_multiple = request.POST.get('allow_multiple_attempts') == 'on'
        show_answers = request.POST.get('show_answers') == 'on'

        assignment = Assignment.objects.create(
            created_by=request.user,
            title=title,
            due_date=due_date,
            allow_multiple_attempts=allow_multiple,
            show_answers=show_answers,
        )
        if worksheet_id:
            assignment.worksheet = get_object_or_404(Worksheet, pk=worksheet_id)
        if workbook_id:
            assignment.workbook = get_object_or_404(Workbook, pk=workbook_id)
        assignment.save()

        for cid in classroom_ids:
            classroom = Classroom.objects.filter(pk=cid, teacher=request.user).first()
            if classroom:
                assignment.classrooms.add(classroom)

        messages.success(request, f'"{assignment.title}" ödevi oluşturuldu.')
        return redirect('assignment_detail', pk=assignment.pk)

    my_worksheets = Worksheet.objects.filter(author=request.user)
    my_workbooks = Workbook.objects.filter(teacher=request.user)
    my_classrooms = Classroom.objects.filter(teacher=request.user)
    return render(request, 'assignments/create.html', {
        'my_worksheets': my_worksheets,
        'my_workbooks': my_workbooks,
        'my_classrooms': my_classrooms,
    })


@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.user.is_teacher and assignment.created_by != request.user:
        messages.error(request, 'Bu ödeve erişim izniniz yok.')
        return redirect('dashboard')
    from apps.submissions.models import Submission
    if request.user.is_teacher:
        submissions = Submission.objects.filter(assignment=assignment).select_related('student')
    else:
        submissions = Submission.objects.filter(assignment=assignment, student=request.user)
    return render(request, 'assignments/detail.html', {
        'assignment': assignment,
        'submissions': submissions,
    })
