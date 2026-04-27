from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import LibraryItem
from apps.worksheets.models import Worksheet, Subject


def library_index(request):
    query = request.GET.get('q', '').strip()
    subject_id = request.GET.get('subject', '')
    level = request.GET.get('level', '')
    language = request.GET.get('language', '')

    items = LibraryItem.objects.select_related('worksheet__author', 'worksheet__subject')

    if query:
        items = items.filter(
            Q(worksheet__title__icontains=query) |
            Q(worksheet__tags__icontains=query) |
            Q(worksheet__author__first_name__icontains=query)
        )
    if subject_id:
        items = items.filter(worksheet__subject_id=subject_id)
    if level:
        items = items.filter(worksheet__level=level)
    if language:
        items = items.filter(worksheet__language=language)

    items = items.order_by('-featured', '-worksheet__view_count')

    subjects = Subject.objects.all()
    return render(request, 'library/index.html', {
        'items': items,
        'subjects': subjects,
        'query': query,
        'level_choices': Worksheet.LEVEL_CHOICES,
        'language_choices': Worksheet.LANGUAGE_CHOICES,
    })


@login_required
def library_publish(request, worksheet_pk):
    worksheet = get_object_or_404(Worksheet, pk=worksheet_pk, author=request.user)
    worksheet.is_public = True
    worksheet.save()
    LibraryItem.objects.get_or_create(worksheet=worksheet)
    messages.success(request, 'Çalışma kağıdı kütüphaneye eklendi.')
    return redirect('library_index')


@login_required
def library_like(request, pk):
    item = get_object_or_404(LibraryItem, pk=pk)
    if request.user in item.likes.all():
        item.likes.remove(request.user)
        liked = False
    else:
        item.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': item.like_count})


@login_required
def library_save(request, pk):
    item = get_object_or_404(LibraryItem, pk=pk)
    if request.user in item.saved_by.all():
        item.saved_by.remove(request.user)
        saved = False
    else:
        item.saved_by.add(request.user)
        saved = True
    return JsonResponse({'saved': saved})
