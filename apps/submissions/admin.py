from django.contrib import admin
from .models import Submission, Answer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('question', 'given_answer', 'is_correct')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'worksheet', 'score', 'correct_count', 'total_questions', 'submitted_at')
    list_filter = ('is_graded',)
    inlines = [AnswerInline]
