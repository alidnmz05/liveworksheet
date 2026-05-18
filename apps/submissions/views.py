from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
import json

from .models import Submission, Answer
from apps.worksheets.models import Worksheet, Question


@login_required
@require_POST
def submit_worksheet(request, worksheet_pk):
    """Öğrencinin gönderdiği yanıtları kaydeder ve puanlar."""
    worksheet = get_object_or_404(Worksheet, pk=worksheet_pk)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Geçersiz veri formatı.'}, status=400)

    assignment_id = data.get('assignment_id') or None
    if not assignment_id and request.user.is_authenticated:
        from apps.assignments.models import Assignment
        pending_assignment = Assignment.objects.filter(
            worksheet=worksheet,
            classrooms__students=request.user
        ).exclude(
            submissions__student=request.user,
            submissions__is_draft=False
        ).order_by('-created_at').first()
        if pending_assignment:
            assignment_id = pending_assignment.id

    is_draft = data.get('is_draft', False)

    with transaction.atomic():
        # Varsa mevcut taslağı bul
        if assignment_id:
            submission = Submission.objects.filter(
                student=request.user, assignment_id=assignment_id, is_draft=True
            ).first()
        else:
            submission = Submission.objects.filter(
                student=request.user, worksheet=worksheet, assignment__isnull=True, is_draft=True
            ).first()

        if not submission:
            submission = Submission.objects.create(
                student=request.user,
                worksheet=worksheet,
                assignment_id=assignment_id,
                is_draft=is_draft,
            )
        else:
            submission.is_draft = is_draft
            submission.answers.all().delete() # Eski taslak yanıtlarını sil

        answers_data = data.get('answers', {})
        for q_id_str, given_answer in answers_data.items():
            try:
                question = Question.objects.get(pk=int(q_id_str), page__worksheet=worksheet)
            except (Question.DoesNotExist, ValueError):
                continue

            if isinstance(given_answer, (dict, list)):
                given_answer = json.dumps(given_answer, ensure_ascii=False)
            else:
                given_answer = str(given_answer)

            answer = Answer.objects.create(
                submission=submission,
                question=question,
                given_answer=given_answer,
            )
            answer.check_answer()

        submission.calculate_score()
        if is_draft:
            submission.is_draft = True
            submission.is_graded = False
            submission.save()

    if is_draft:
        return JsonResponse({'success': True, 'message': 'Taslak olarak kaydedildi.'})

    # Puanlama sistemine göre gösterilecek skoru hesapla
    grading_system = worksheet.grading_system  # '100' veya '10'
    if grading_system == '10':
        display_score = round((submission.score / 10), 1) if submission.score is not None else 0
    else:
        display_score = submission.score  # zaten 0-100

    return JsonResponse({
        'submission_id': submission.id,
        'score': submission.score,           # her zaman 0-100 (ham oran)
        'display_score': display_score,      # gösterilecek puan (sisteme göre)
        'grading_system': grading_system,    # '10' veya '100'
        'correct': submission.correct_count,
        'total': submission.total_questions,
        'answers': [
            {
                'question_id': a.question_id,
                'is_correct': a.is_correct,
                'correct_answer': a.question.get_correct_answer_text(),
                'ai_score': a.ai_score,
                'ai_feedback': a.ai_feedback,
            }
            for a in submission.answers.select_related('question')
        ]
    })


@login_required
def submission_detail(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    if submission.student != request.user and not request.user.is_teacher:
        messages.error(request, 'Bu sonuca erişim izniniz yok.')
        return redirect('dashboard')
    answers = submission.answers.select_related('question').order_by('question__order')
    return render(request, 'submissions/detail.html', {
        'submission': submission,
        'answers': answers,
    })


@login_required
def my_submissions(request):
    submissions = Submission.objects.filter(student=request.user).select_related('worksheet')
    return render(request, 'submissions/list.html', {'submissions': submissions})
