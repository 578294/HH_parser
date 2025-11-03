# hhparser/views.py
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.utils import timezone  # ДОБАВЬТЕ ЭТОТ ИМПОРТ
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
                return JsonResponse({'success': False, 'error': 'Не удалось получить данные'})

            saved_count = parser.save_to_database(vacancies_data)

            return JsonResponse({
                'success': True,
                'found': len(vacancies_data),
                'saved': saved_count,
                'message': f'Найдено {len(vacancies_data)} вакансий, сохранено {saved_count}'
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Ошибка: {str(e)}'})


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
            'vacancies_count': vacancies.count(),
            'current_filters': request.GET.dict()
        })


class FilterVacanciesView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        try:
            data = json.loads(request.body)
            filters = data.get('filters', {})

            vacancies = Vacancy.objects.all().order_by('-created_at')
            filtered_vacancies = []

            for vacancy in vacancies:
                if self.matches_filters(vacancy, filters):
                    filtered_vacancies.append({
                        'id': vacancy.id,
                        'title': vacancy.title,
                        'company': vacancy.company,
                        'salary': vacancy.salary,
                        'experience': vacancy.get_experience_display(),
                        'employment': vacancy.get_employment_display(),
                        'description': vacancy.description,
                        'link': vacancy.link,
                        'created_at': vacancy.created_at
                    })

            return JsonResponse({
                'success': True,
                'vacancies': filtered_vacancies,
                'count': len(filtered_vacancies)
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def matches_filters(self, vacancy, filters):
        """Простая проверка фильтров"""
        if filters.get('keywords'):
            keywords = filters['keywords'].lower()
            if (keywords not in vacancy.title.lower() and
                    keywords not in vacancy.company.lower() and
                    keywords not in vacancy.description.lower()):
                return False

        if filters.get('min_salary'):
            try:
                min_salary = int(filters['min_salary'])
                if "Не указана" not in vacancy.salary:
                    salary_num = ''.join(filter(str.isdigit, vacancy.salary))
                    if salary_num and int(salary_num) < min_salary:
                        return False
            except:
                pass

        if filters.get('experience') and filters['experience'] != '':
            if vacancy.experience != filters['experience']:
                return False

        if filters.get('employment') and filters['employment'] != '':
            if vacancy.employment != filters['employment']:
                return False

        return True


class GenerateLetterView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        try:
            data = json.loads(request.body)
            vacancy_id = data.get('vacancy_id')
            template_type = data.get('template_type', 'standard')
            custom_text = data.get('custom_text', '')

            vacancy = Vacancy.objects.get(id=vacancy_id)

            # Простой генератор писем
            letter_content = f"Уважаемые представители {vacancy.company}!\n\nЯ пишу о вакансии '{vacancy.title}'.\n\nС уважением!"

            return JsonResponse({
                'success': True,
                'letter_content': letter_content
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class GetVacanciesView(View):
    def get(self, request):
        vacancies = Vacancy.objects.all().order_by('-created_at')[:50]

        vacancy_list = []
        for vacancy in vacancies:
            vacancy_list.append({
                'id': vacancy.id,
                'title': vacancy.title,
                'company': vacancy.company,
                'salary': vacancy.salary,
                'experience': vacancy.get_experience_display(),
                'employment': vacancy.get_employment_display(),
                'link': vacancy.link,
            })

        return JsonResponse({'vacancies': vacancy_list})


class StatisticsView(View):
    def get(self, request):
        total_vacancies = Vacancy.objects.count()
        recent_count = Vacancy.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).count()

        return JsonResponse({
            'total_vacancies': total_vacancies,
            'recent_vacancies': recent_count
        })