from django.contrib import admin
from .models import User, Classroom


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'role', 'school', 'created_at')
    list_filter = ('role',)
    search_fields = ('email', 'first_name', 'last_name')


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'code', 'created_at')
    search_fields = ('name', 'code')
