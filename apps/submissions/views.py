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
    assignment_id = request.POST.get('assignment_id') or None

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Geçersiz veri formatı.'}, status=400)

    with transaction.atomic():
        submission = Submission.objects.create(
            student=request.user,
            worksheet=worksheet,
            assignment_id=assignment_id,
        )

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

    return JsonResponse({
        'submission_id': submission.id,
        'score': submission.score,
        'correct': submission.correct_count,
        'total': submission.total_questions,
        'answers': [
            {
                'question_id': a.question_id,
                'is_correct': a.is_correct,
                'correct_answer': a.question.correct_answer,
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
