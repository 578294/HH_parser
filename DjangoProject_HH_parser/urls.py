# DjangoProject_HH_parser/urls.py
from django.contrib import admin
from django.urls import path
from hhparser.views import (IndexView, ParserView, VacancyListView, StatisticsView,
                           GenerateLetterView, GetVacanciesView, FilterVacanciesView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('parser/', ParserView.as_view(), name='parser'),
    path('vacancies/', VacancyListView.as_view(), name='vacancy_list'),
    path('api/generate-letter/', GenerateLetterView.as_view(), name='generate_letter'),
    path('api/vacancies/', GetVacanciesView.as_view(), name='api_vacancies'),
    path('api/filter-vacancies/', FilterVacanciesView.as_view(), name='filter_vacancies'),
    path('api/statistics/', StatisticsView.as_view(), name='api_statistics'),
]