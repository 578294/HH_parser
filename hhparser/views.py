#from django.shortcuts import render

# def index(request):
#     if request.method == 'POST':
#         url = request.POST.get('sourceUrl')
#         print(url)
#     return render(request, 'parser/html/index.html')
#
# def SPindex(request):
#     return render(request, 'parser/html/SPindex.html')
#
# def HPindex(request):
#     return render(request, 'parser/html/HPindex.html')
#
# def WHindex(request):
#     return render(request, 'parser/html/WHindex.html')


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from django.contrib import messages
from models import Vacancy, CoverLetter
from services.hh_parser import HHApiParser
import json


class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')


class ParserView(View):
    def get(self, request):
        vacancies = Vacancy.objects.all().order_by('-created_at')[:50]
        return render(request, 'parser.html', {'vacancies': vacancies})

    def post(self, request):
        search_query = request.POST.get('search_query', 'python')
        pages = int(request.POST.get('pages', 1))

        try:
            parser = HHApiParser()
            vacancies_data = parser.parse_vacancies(search_query, pages)
            saved_count = parser.save_to_database(vacancies_data)

            return JsonResponse({
                'success': True,
                'found': len(vacancies_data),
                'saved': saved_count,
                'message': f'Найдено {len(vacancies_data)} вакансий, сохранено {saved_count}'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class VacancyListView(View):
    def get(self, request):
        vacancies = Vacancy.objects.all().order_by('-created_at')
        return render(request, 'vacancy_list.html', {'vacancies': vacancies})


class StyleView(View):
    def get(self, request, style):
        templates = {
            'HP': 'HPindex.html',
            'SP': 'SPindex.html',
            'WH': 'WHindex.html'
        }
        template = templates.get(style, 'index.html')
        vacancies = Vacancy.objects.all().order_by('-created_at')[:20]
        return render(request, template, {'vacancies': vacancies})