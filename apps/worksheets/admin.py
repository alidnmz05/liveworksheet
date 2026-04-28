from django.contrib import admin
from .models import Worksheet, WorksheetPage, Question, Subject, ChoiceOption


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)


class WorksheetPageInline(admin.TabularInline):
    model = WorksheetPage
    extra = 0


@admin.register(Worksheet)
class WorksheetAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'subject', 'level', 'is_public', 'view_count', 'created_at')
    list_filter = ('is_public', 'level', 'language')
    search_fields = ('title', 'author__email')
    inlines = [WorksheetPageInline]


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0


@admin.register(WorksheetPage)
class WorksheetPageAdmin(admin.ModelAdmin):
    list_display = ('worksheet', 'order')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('page', 'question_type', 'order', 'correct_answer')
    list_filter = ('question_type',)
