from django.contrib import admin
from .models import LibraryItem


@admin.register(LibraryItem)
class LibraryItemAdmin(admin.ModelAdmin):
    list_display = ('worksheet', 'featured', 'like_count', 'added_at')
    list_filter = ('featured',)
    filter_horizontal = ('likes', 'saved_by')
