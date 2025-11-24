"""
Модуль views.py содержит представления Django для приложения hhparser.

Основные представления:
- VacancyListView: отображение и фильтрация списка вакансий
- ParserView: управление процессом парсинга вакансий
- API представления: REST endpoints для работы с вакансиями
"""

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.urls import reverse
from .models import Vacancy
from DjangoProject_HH_parser.Services.hh_parser import HHApiParser
import json
import re

# Константы URL
VACANCIES_URL = '/vacancies/'
INDEX_URL = '/'
PARSER_URL = '/parser/'
API_FILTER_URL = '/api/filter/'
API_GENERATE_LETTER_URL = '/api/generate-letter/'
API_GET_VACANCIES_URL = '/api/vacancies/'
API_STATISTICS_URL = '/api/statistics/'


class VacancyFilter:
    """Класс для фильтрации вакансий"""

    def __init__(self, queryset):
        self.queryset = queryset

    def apply_search_filter(self, search_query):
        """Применяет поиск по всем текстовым полям"""
        if search_query:
            self.queryset = self.queryset.filter(
                Q(title__icontains=search_query) |
                Q(company__icontains=search_query) |
                Q(skills__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        return self

    def apply_keywords_filter(self, keywords):
        """Применяет фильтр по ключевым словам"""
        if keywords:
            self.queryset = self.queryset.filter(
                Q(title__icontains=keywords) |
                Q(company__icontains=keywords) |
                Q(skills__icontains=keywords) |
                Q(description__icontains=keywords)
            )
        return self

    def apply_salary_filter(self, min_salary):
        """Применяет фильтр по минимальной зарплате"""
        if min_salary:
            try:
                min_salary_val = int(min_salary)
                salary_filter = Q()
                salary_filter |= Q(salary__icontains=f"от {min_salary_val}")
                salary_filter |= Q(salary__icontains=f"{min_salary_val} -")
                salary_filter |= Q(salary__regex=rf'{min_salary_val}')
                self.queryset = self.queryset.filter(salary_filter)
            except ValueError:
                pass
        return self

    def apply_experience_filter(self, experience):
        """Применяет фильтр по опыту работы"""
        if experience and experience != '':
            self.queryset = self.queryset.filter(experience=experience)
        return self

    def apply_employment_filter(self, employment):
        """Применяет фильтр по типу занятости"""
        if employment and employment != '':
            self.queryset = self.queryset.filter(employment=employment)
        return self

    def apply_min_experience_filter(self, min_experience_years):
        """Применяет фильтр по минимальному количеству лет опыта"""
        if min_experience_years:
            try:
                min_years = int(min_experience_years)
                experience_map = {
                    'no': 0,
                    '1-3': 2,
                    '3-6': 4,
                    '6+': 7
                }

                valid_experiences = []
                for exp_code, years in experience_map.items():
                    if years >= min_years:
                        valid_experiences.append(exp_code)

                if valid_experiences:
                    self.queryset = self.queryset.filter(experience__in=valid_experiences)
            except ValueError:
                pass
        return self

    def get_queryset(self):
        """Возвращает отфильтрованный queryset"""
        return self.queryset


class VacancyListView(View):
    """
    Представление для отображения и фильтрации списка вакансий.
    """

    def get(self, request) -> render:
        """
        Обработка GET-запросов для отображения отфильтрованных вакансий.
        """
        # Получаем параметры фильтрации
        filter_params = self._get_filter_params(request)

        # Применяем фильтры
        vacancies = self._apply_filters(filter_params)

        # Пагинация
        paginator = Paginator(vacancies.order_by('-created_at'), 20)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        return render(request, 'parser/html/vacancies.html', {
            'vacancies': page_obj,
            'page_obj': page_obj,
            'vacancies_count': vacancies.count(),
            'has_active_filters': self._has_active_filters(filter_params),
            **filter_params
        })

    def _get_filter_params(self, request) -> dict:
        """Извлекает параметры фильтрации из запроса"""
        return {
            'search_query': request.GET.get('search', ''),
            'keywords': request.GET.get('keywords', ''),
            'min_salary': request.GET.get('min_salary', ''),
            'experience': request.GET.get('experience', ''),
            'employment': request.GET.get('employment', ''),
            'min_experience_years': request.GET.get('min_experience_years', ''),
        }

    def _apply_filters(self, filter_params: dict):
        """Применяет все фильтры к queryset"""
        filter_instance = VacancyFilter(Vacancy.objects.all())

        filter_instance \
            .apply_search_filter(filter_params['search_query']) \
            .apply_keywords_filter(filter_params['keywords']) \
            .apply_salary_filter(filter_params['min_salary']) \
            .apply_experience_filter(filter_params['experience']) \
            .apply_employment_filter(filter_params['employment']) \
            .apply_min_experience_filter(filter_params['min_experience_years'])

        return filter_instance.get_queryset()

    def _has_active_filters(self, filter_params: dict) -> bool:
        """Проверяет наличие активных фильтров"""
        return any([
            filter_params['keywords'],
            filter_params['min_salary'],
            filter_params['experience'] and filter_params['experience'] != '',
            filter_params['employment'] and filter_params['employment'] != '',
            filter_params['min_experience_years']
        ])


class IndexView(View):
    """
    Представление для главной страницы приложения.
    """

    def get(self, request) -> render:
        """
        Обработка GET-запросов для главной страницы.
        """
        total_vacancies = Vacancy.objects.count()
        recent_vacancies = Vacancy.objects.all().order_by('-created_at')[:5]

        return render(request, 'parser/html/index.html', {
            'total_vacancies': total_vacancies,
            'recent_vacancies': recent_vacancies
        })


class ParserView(View):
    """
    Представление для управления процессом парсинга вакансий.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """Отключает CSRF защиту для API запросов."""
        return super().dispatch(*args, **kwargs)

    def get(self, request) -> render:
        """
        Обработка GET-запросов для страницы парсинга.
        """
        total_vacancies = Vacancy.objects.count()
        return render(request, 'parser/html/parser.html', {
            'total_vacancies': total_vacancies
        })

    def post(self, request) -> JsonResponse:
        """
        Обработка запроса на запуск парсинга вакансий.
        """
        try:
            # Извлекаем данные
            data = self._extract_request_data(request)

            # Парсим вакансии
            vacancies_data = self._parse_vacancies(data['search_query'], data['vacancy_count'])
            if not vacancies_data:
                return JsonResponse({'success': False, 'error': 'Не удалось получить данные'})

            # Применяем фильтры
            filtered_data = self._apply_user_filters(vacancies_data, data['filters'])

            # Сохраняем в БД
            processed_count = self._save_to_database(filtered_data)

            # Формируем ответ
            return self._build_success_response(filtered_data, processed_count, data['filters'], data['search_query'])

        except Exception as e:
            return self._handle_error(e)

    def _extract_request_data(self, request) -> dict:
        """Извлекает данные из запроса"""
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            return {
                'search_query': data.get('query', 'Python'),
                'vacancy_count': int(data.get('vacancy_count', 50)),
                'filters': {
                    'keywords': data.get('keywords', ''),
                    'min_salary': data.get('min_salary', ''),
                    'experience': data.get('experience', ''),
                    'min_experience_years': data.get('min_experience_years', ''),
                    'employment': data.get('employment', ''),
                }
            }
        else:
            return {
                'search_query': request.POST.get('query', 'Python'),
                'vacancy_count': int(request.POST.get('vacancy_count', 50)),
                'filters': {
                    'keywords': request.POST.get('keywords', ''),
                    'min_salary': request.POST.get('min_salary', ''),
                    'experience': request.POST.get('experience', ''),
                    'min_experience_years': request.POST.get('min_experience_years', ''),
                    'employment': request.POST.get('employment', ''),
                }
            }

    def _parse_vacancies(self, search_query: str, vacancy_count: int) -> list:
        """Парсит вакансии через API"""
        parser = HHApiParser()
        vacancies_data = parser.parse_vacancies(search_query, vacancy_count)

        if vacancies_data:
            vacancies_data = [v for v in vacancies_data if v is not None]
            print(f"📥 Получено вакансий от API: {len(vacancies_data)}")

        return vacancies_data

    def _apply_user_filters(self, vacancies_data: list, filters: dict) -> list:
        """Применяет пользовательские фильтры"""
        if not any(filters.values()):
            return vacancies_data

        filter_view = FilterVacanciesView()
        filtered_vacancies = []

        for vacancy in vacancies_data:
            temp_vacancy = self._create_temp_vacancy(vacancy)
            if filter_view.matches_filters(temp_vacancy, filters):
                filtered_vacancies.append(vacancy)

        print(f"🎯 После пользовательских фильтров: {len(filtered_vacancies)} вакансий")
        return filtered_vacancies

    def _create_temp_vacancy(self, vacancy_data: dict):
        """Создает временный объект вакансии для фильтрации"""
        class TempVacancy:
            def __init__(self, data):
                self.title = data.get('title', '')
                self.company = data.get('company', '')
                self.salary = data.get('salary', '')
                self.description = data.get('description', '')
                self.experience = data.get('experience', '')
                self.employment = data.get('employment', '')
                self.skills = data.get('skills', '')
                self.link = data.get('link', '')

        return TempVacancy(vacancy_data)

    def _save_to_database(self, vacancies_data: list) -> int:
        """Сохраняет вакансии в базу данных"""
        parser = HHApiParser()
        return parser.save_to_database(vacancies_data)

    def _build_success_response(self, vacancies_data: list, processed_count: int,
                               filters: dict, search_query: str) -> JsonResponse:
        """Формирует успешный JSON ответ"""
        filter_url = self._build_filter_url(filters, search_query)
        has_active_filters = any(filters.values())

        return JsonResponse({
            'success': True,
            'found': len(vacancies_data),
            'saved': processed_count,
            'message': f'Найдено {len(vacancies_data)} вакансий, обработано {processed_count}',
            'filter_url': filter_url,
            'has_filters': has_active_filters and len(vacancies_data) > 0
        })

    def _build_filter_url(self, filters: dict, search_query: str) -> str:
        """Строит URL для фильтрации"""
        filter_params = {}

        for key in ['keywords', 'min_salary', 'experience', 'employment', 'min_experience_years']:
            if filters.get(key):
                filter_params[key] = filters[key]

        if search_query and search_query != 'Python':
            filter_params['search'] = search_query

        filter_url = VACANCIES_URL
        if filter_params:
            filter_url += '?' + '&'.join([f"{k}={v}" for k, v in filter_params.items() if v])

        return filter_url

    def _handle_error(self, error: Exception) -> JsonResponse:
        """Обрабатывает ошибки"""
        print(f"Ошибка в ParserView: {str(error)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': f'Ошибка: {str(error)}'})


class FilterVacanciesView(View):
    """
    API представление для фильтрации вакансий через JSON API.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """Отключает CSRF защиту для API запросов."""
        return super().dispatch(*args, **kwargs)

    def post(self, request) -> JsonResponse:
        """
        Обработка POST-запросов для фильтрации вакансий через API.
        """
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
                        'experience': self.get_experience_display(vacancy.experience),
                        'employment': self.get_employment_display(vacancy.employment),
                        'description': vacancy.description,
                        'link': vacancy.link,
                        'created_at': vacancy.created_at.strftime('%d.%m.%Y %H:%M')
                    })

            return JsonResponse({
                'success': True,
                'vacancies': filtered_vacancies,
                'count': len(filtered_vacancies)
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def get_experience_display(self, experience_code: str) -> str:
        """
        Преобразует код опыта работы в читаемое отображение.
        """
        experience_map = {
            'no': 'Нет опыта',
            '1-3': '1-3 года',
            '3-6': '3-6 лет',
            '6+': 'Более 6 лет'
        }
        return experience_map.get(experience_code, experience_code)

    def get_employment_display(self, employment_code: str) -> str:
        """
        Преобразует код типа занятости в читаемое отображение.
        """
        employment_map = {
            'full': 'Полная занятость',
            'part': 'Частичная занятость',
            'remote': 'Удаленная работа',
            'project': 'Проектная работа'
        }
        return employment_map.get(employment_code, employment_code)

    def matches_filters(self, vacancy, filters: dict) -> bool:
        """
        Проверяет соответствие вакансии заданным фильтрам.
        """
        # Фильтр по ключевым словам
        if filters.get('keywords'):
            keywords = filters['keywords'].lower().strip()
            if keywords:
                search_fields = [
                    getattr(vacancy, 'title', '').lower(),
                    getattr(vacancy, 'company', '').lower(),
                    getattr(vacancy, 'description', '').lower(),
                    getattr(vacancy, 'skills', '').lower()
                ]

                keyword_found = any(keywords in field for field in search_fields if field)
                if not keyword_found:
                    return False

        # Фильтр по минимальной зарплате
        if filters.get('min_salary'):
            try:
                min_salary = int(filters['min_salary'])
                salary_text = getattr(vacancy, 'salary', '')

                if salary_text and "Не указана" not in salary_text:
                    numbers = re.findall(r'\d+', salary_text.replace(' ', '').replace(',', ''))
                    if numbers:
                        salary_value = max(map(int, numbers))
                        if salary_value < min_salary:
                            return False
            except (ValueError, TypeError):
                pass

        # Фильтр по опыту работы
        if filters.get('experience') and filters['experience'] != '':
            vacancy_experience = getattr(vacancy, 'experience', '')
            if vacancy_experience != filters['experience']:
                return False

        # Фильтр по типу занятости
        if filters.get('employment') and filters['employment'] != '':
            vacancy_employment = getattr(vacancy, 'employment', '')
            if vacancy_employment != filters['employment']:
                return False

        # Фильтр по минимальному количеству лет опыта
        if filters.get('min_experience_years'):
            try:
                min_years = int(filters['min_experience_years'])
                vacancy_experience = getattr(vacancy, 'experience', '')
                experience_years = self.get_experience_years(vacancy_experience)

                if experience_years < min_years:
                    return False
            except (ValueError, TypeError):
                pass

        return True

    def get_experience_years(self, experience_code: str) -> int:
        """
        Конвертирует код опыта в количество лет для численного сравнения.
        """
        experience_map = {
            'no': 0,
            '1-3': 2,
            '3-6': 4,
            '6+': 7
        }
        return experience_map.get(experience_code, 0)


class GenerateLetterView(View):
    """
    API представление для генерации сопроводительных писем.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """Отключает CSRF защиту для API запросов."""
        return super().dispatch(*args, **kwargs)

    def post(self, request) -> JsonResponse:
        """
        Обработка POST-запросов для генерации сопроводительного письма.
        """
        try:
            data = json.loads(request.body)
            vacancy_id = data.get('vacancy_id')
            template_type = data.get('template_type', 'standard')
            custom_text = data.get('custom_text', '')

            vacancy = Vacancy.objects.get(id=vacancy_id)

            letter_content = f"""Уважаемые представители компании {vacancy.company}!

Я пишу в ответ на вакансию "{vacancy.title}", размещенную на HH.ru.

Мой опыт и навыки идеально подходят для этой позиции. 
Я заинтересован в возможности присоединиться к вашей команде и внести свой вклад в развитие компании.

Готов обсудить детали сотрудничества на собеседовании.

С уважением,
[Ваше Имя]
[Ваш телефон]
[Ваш email]"""

            return JsonResponse({
                'success': True,
                'letter_content': letter_content
            })

        except Vacancy.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Вакансия не найдена'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class GetVacanciesView(View):
    """
    API представление для получения списка вакансий в JSON формате.
    """

    def get(self, request) -> JsonResponse:
        """
        Обработка GET-запросов для получения списка вакансий.
        """
        try:
            vacancies = Vacancy.objects.all().order_by('-created_at')[:50]

            vacancy_list = []
            for vacancy in vacancies:
                vacancy_list.append({
                    'id': vacancy.id,
                    'title': vacancy.title,
                    'company': vacancy.company,
                    'salary': vacancy.salary,
                    'experience': vacancy.experience,
                    'employment': vacancy.employment,
                    'link': vacancy.link,
                    'created_at': vacancy.created_at.strftime('%d.%m.%Y %H:%M')
                })

            return JsonResponse({'vacancies': vacancy_list})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class StatisticsView(View):
    """
    API представление для получения статистики по вакансиям.
    """

    def get(self, request) -> JsonResponse:
        """
        Обработка GET-запросов для получения статистических данных.
        """
        try:
            total_vacancies = Vacancy.objects.count()
            recent_count = Vacancy.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count()

            experience_stats = {
                'no': Vacancy.objects.filter(experience='no').count(),
                '1-3': Vacancy.objects.filter(experience='1-3').count(),
                '3-6': Vacancy.objects.filter(experience='3-6').count(),
                '6+': Vacancy.objects.filter(experience='6+').count(),
            }

            employment_stats = {
                'full': Vacancy.objects.filter(employment='full').count(),
                'part': Vacancy.objects.filter(employment='part').count(),
                'remote': Vacancy.objects.filter(employment='remote').count(),
                'project': Vacancy.objects.filter(employment='project').count(),
            }

            return JsonResponse({
                'total_vacancies': total_vacancies,
                'recent_vacancies': recent_count,
                'experience_stats': experience_stats,
                'employment_stats': employment_stats
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})