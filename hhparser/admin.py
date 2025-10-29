from django.contrib import admin
from hhparser.models import Vacancy, CoverLetter


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'salary', 'experience', 'employment', 'created_at']
    list_filter = ['experience', 'employment', 'created_at']
    search_fields = ['title', 'company', 'description']
    readonly_fields = ['created_at', 'hp_title', 'sp_title', 'wh_title']

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'company', 'salary', 'description', 'experience', 'employment', 'skills', 'link')
        }),
        ('Стиль Гарри Поттер', {
            'fields': ('hp_title', 'hp_company', 'hp_salary'),
            'classes': ('collapse',)
        }),
        ('Стиль South Park', {
            'fields': ('sp_title', 'sp_company', 'sp_salary'),
            'classes': ('collapse',)
        }),
        ('Стиль Warhammer', {
            'fields': ('wh_title', 'wh_company', 'wh_salary'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CoverLetter)
class CoverLetterAdmin(admin.ModelAdmin):
    list_display = ['title', 'template_type', 'style', 'vacancy', 'created_at']
    list_filter = ['template_type', 'style', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at']