from django.contrib import admin
from .models import Workbook, WorkbookPage


class WorkbookPageInline(admin.TabularInline):
    model = WorkbookPage
    extra = 0


@admin.register(Workbook)
class WorkbookAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'is_public', 'created_at')
    inlines = [WorkbookPageInline]
