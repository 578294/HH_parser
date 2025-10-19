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


from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from .models import Vacancy
from DjangoProject_HH_parser.Services.hh_parser import HHApiParser
import json

class IndexView(View):
    def get(self, request):
        total_vacancies = Vacancy.objects.count()
        recent_vacancies = Vacancy.objects.all().order_by('-created_at')[:5]

        return render(request, 'parser/html/index.html', {
            'total_vacancies': total_vacancies,
            'recent_vacancies': recent_vacancies
        })


class ParserView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        return render(request, 'parser/html/parser.html')

    def post(self, request):
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                search_query = data.get('query', 'Python')
                pages = int(data.get('pages', 1))
            else:
                search_query = request.POST.get('query', 'Python')
                pages = int(request.POST.get('pages', 1))

            parser = HHApiParser()
            vacancies_data = parser.parse_vacancies(search_query, pages)

            if not vacancies_data:
                return JsonResponse({
                    'success': False,
                    'error': 'Не удалось получить данные с HH.ru'
                })

            saved_count = parser.save_to_database(vacancies_data)

            return JsonResponse({
                'success': True,
                'found': len(vacancies_data),
                'saved': saved_count,
                'message': f'Успешно! Найдено {len(vacancies_data)} вакансий, сохранено {saved_count}'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Ошибка при парсинге: {str(e)}'
            })


class VacancyListView(View):
    def get(self, request):
        search_query = request.GET.get('search', '')

        if search_query:
            vacancies = Vacancy.objects.filter(
                Q(title__icontains=search_query) |
                Q(company__icontains=search_query) |
                Q(skills__icontains=search_query)
            ).order_by('-created_at')
        else:
            vacancies = Vacancy.objects.all().order_by('-created_at')

        return render(request, 'parser/html/vacancies.html', {
            'vacancies': vacancies,
            'search_query': search_query,
            'vacancies_count': vacancies.count()
        })


class StyleView(View):
    def get(self, request, style):
        """Переключение между стилями интерфейса"""
        templates = {
            'HP': 'parser/html/HPindex.html',
            'SP': 'parser/html/SPindex.html',
            'WH': 'parser/html/WHindex.html'
        }

        template_name = templates.get(style, 'parser/html/index.html')
        vacancies = Vacancy.objects.all().order_by('-created_at')[:10]

        return render(request, template_name, {
            'vacancies': vacancies,
            'current_style': style,
            'total_vacancies': Vacancy.objects.count()
        })