# hhparser/admin.py
from django.contrib import admin
from hhparser.models import Vacancy  # Убираем CoverLetter

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'salary', 'experience', 'employment', 'created_at']
    list_filter = ['experience', 'employment', 'created_at']
    search_fields = ['title', 'company', 'description']
    readonly_fields = ['created_at']

# Закомментируем или удалим блок с CoverLetter
# @admin.register(CoverLetter)
# class CoverLetterAdmin(admin.ModelAdmin):
#     list_display = ['title', 'created_at']
#     search_fields = ['title', 'created_at']
#     readonly_fields = ['created_at']