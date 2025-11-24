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
from .models import Vacancy
from DjangoProject_HH_parser.Services.hh_parser import HHApiParser
import json
import re

FILTER_URL = '/vacancies/'

class VacancyListView(View):
    """
    Представление для отображения и фильтрации списка вакансий.

    Поддерживает сложную систему фильтрации по ключевым словам, зарплате,
    опыту работы и типу занятости с пагинацией результатов.
    """

    def get(self, request) -> render:
        """
        Обработка GET-запросов для отображения отфильтрованных вакансий.

        Применяет фильтры из параметров запроса и формирует paginated response.
        Поддерживает поиск по всем текстовым полям и сложные условия фильтрации.

        Args:
            request: HttpRequest (объект запроса с параметрами фильтрации)

        Returns:
            HttpResponse: отрендеренный шаблон с пагинированными вакансиями
        """
        # Получаем параметры фильтрации
        search_query = request.GET.get('search', '')
        keywords = request.GET.get('keywords', '')
        min_salary = request.GET.get('min_salary', '')
        experience = request.GET.get('experience', '')
        employment = request.GET.get('employment', '')
        min_experience_years = request.GET.get('min_experience_years', '')

        # Начинаем с всех вакансий
        vacancies = Vacancy.objects.all().order_by('-created_at')

        # Базовый поиск по всем текстовым полям
        if search_query:
            vacancies = vacancies.filter(
                Q(title__icontains=search_query) |
                Q(company__icontains=search_query) |
                Q(skills__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Фильтр по ключевым словам
        if keywords:
            vacancies = vacancies.filter(
                Q(title__icontains=keywords) |
                Q(company__icontains=keywords) |
                Q(skills__icontains=keywords) |
                Q(description__icontains=keywords)
            )

        # Фильтр по минимальной зарплате
        if min_salary:
            try:
                min_salary_val = int(min_salary)
                # Ищем вакансии с зарплатой от указанной суммы
                salary_filter = Q()
                salary_filter |= Q(salary__icontains=f"от {min_salary_val}")
                salary_filter |= Q(salary__icontains=f"{min_salary_val} -")
                salary_filter |= Q(salary__regex=rf'{min_salary_val}')
                vacancies = vacancies.filter(salary_filter)
            except ValueError:
                pass  # Если не число, игнорируем фильтр

        # Фильтр по опыту работы
        if experience and experience != '':
            vacancies = vacancies.filter(experience=experience)

        # Фильтр по типу занятости
        if employment and employment != '':
            vacancies = vacancies.filter(employment=employment)

        # Фильтр по минимальному количеству лет опыта
        if min_experience_years:
            try:
                min_years = int(min_experience_years)
                # Сопоставляем коды опыта с годами
                experience_map = {
                    'no': 0,
                    '1-3': 2,  # среднее значение диапазона
                    '3-6': 4,  # среднее значение диапазона
                    '6+': 7  # минимальное значение для "более 6 лет"
                }

                # Находим подходящие уровни опыта
                valid_experiences = []
                for exp_code, years in experience_map.items():
                    if years >= min_years:
                        valid_experiences.append(exp_code)

                # Применяем фильтр
                if valid_experiences:
                    vacancies = vacancies.filter(experience__in=valid_experiences)
            except ValueError:
                pass  # Если не число, игнорируем фильтр

        # Проверяем, есть ли активные фильтры
        has_active_filters = any([
            keywords,
            min_salary,
            experience and experience != '',
            employment and employment != '',
            min_experience_years
        ])

        # ПАГИНАЦИЯ - разбиваем на страницы
        paginator = Paginator(vacancies, 20)  # 20 вакансий на страницу
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        return render(request, 'parser/html/vacancies.html', {
            'vacancies': page_obj,  # Теперь передаем только вакансии текущей страницы
            'page_obj': page_obj,  # Объект пагинации для навигации
            'search_query': search_query,
            'keywords': keywords,
            'min_salary': min_salary,
            'experience': experience,
            'employment': employment,
            'min_experience_years': min_experience_years,
            'vacancies_count': vacancies.count(),  # Общее количество после фильтрации
            'has_active_filters': has_active_filters
        })


class IndexView(View):
    """
    Представление для главной страницы приложения.

    Отображает общую статистику и последние добавленные вакансии.
    """

    def get(self, request) -> render:
        """
        Обработка GET-запросов для главной страницы.

        Args:
            request: HttpRequest (объект запроса)

        Returns:
            HttpResponse: отрендеренный шаблон главной страницы
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

    Обеспечивает взаимодействие между фронтендом и парсером.
    Поддерживает как form-data, так и JSON запросы.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """Отключает CSRF защиту для API запросов."""
        return super().dispatch(*args, **kwargs)

    def get(self, request) -> render:
        """
        Обработка GET-запросов для страницы парсинга.

        Args:
            request: HttpRequest (объект запроса)

        Returns:
            HttpResponse: отрендеренный шаблон страницы парсинга
        """
        total_vacancies = Vacancy.objects.count()
        return render(request, 'parser/html/parser.html', {
            'total_vacancies': total_vacancies
        })

    def post(self, request) -> JsonResponse:
        """
        Обработка запроса на запуск парсинга вакансий.

        Получает параметры парсинга, запускает парсер и применяет фильтры.
        Сохраняет результаты в базу данных и возвращает статистику обработки.

        Args:
            request: HttpRequest (объект запроса с параметрами парсинга)

        Returns:
            JsonResponse: результат операции со статистикой и ссылкой на результаты
        """
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                search_query = data.get('query', 'Python')
                vacancy_count = int(data.get('vacancy_count', 50))
                filters = {
                    'keywords': data.get('keywords', ''),
                    'min_salary': data.get('min_salary', ''),
                    'experience': data.get('experience', ''),
                    'min_experience_years': data.get('min_experience_years', ''),
                    'employment': data.get('employment', ''),
                }
            else:
                search_query = request.POST.get('query', 'Python')
                vacancy_count = int(request.POST.get('vacancy_count', 50))
                filters = {
                    'keywords': request.POST.get('keywords', ''),
                    'min_salary': request.POST.get('min_salary', ''),
                    'experience': request.POST.get('experience', ''),
                    'min_experience_years': request.POST.get('min_experience_years', ''),
                    'employment': request.POST.get('employment', ''),
                }

            parser = HHApiParser()
            vacancies_data = parser.parse_vacancies(search_query, vacancy_count)

            if not vacancies_data:
                return JsonResponse({'success': False, 'error': 'Не удалось получить данные'})

            print(f"📥 Получено вакансий от API: {len(vacancies_data)}")

            # Фильтруем None значения
            vacancies_data = [v for v in vacancies_data if v is not None]
            print(f"📊 После фильтрации None: {len(vacancies_data)} вакансий")

            # Применяем пользовательские фильтры
            filtered_vacancies = []
            has_active_filters = any(filters.values())

            if has_active_filters:
                filter_view = FilterVacanciesView()

                for vacancy in vacancies_data:
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

                    temp_vacancy = TempVacancy(vacancy)
                    if filter_view.matches_filters(temp_vacancy, filters):
                        filtered_vacancies.append(vacancy)

                vacancies_data = filtered_vacancies
                print(f"🎯 После пользовательских фильтров: {len(vacancies_data)} вакансий")

            # Сохраняем в базу
            processed_count = parser.save_to_database(vacancies_data)

            # Формируем URL для просмотра отфильтрованных вакансий
            filter_params = {}
            if filters.get('keywords'):
                filter_params['keywords'] = filters['keywords']
            if filters.get('min_salary'):
                filter_params['min_salary'] = filters['min_salary']
            if filters.get('experience'):
                filter_params['experience'] = filters['experience']
            if filters.get('employment'):
                filter_params['employment'] = filters['employment']
            if filters.get('min_experience_years'):
                filter_params['min_experience_years'] = filters['min_experience_years']

            # Добавляем поисковый запрос как параметр
            if search_query and search_query != 'Python':
                filter_params['search'] = search_query

            filter_url = FILTER_URL
            if filter_params:
                filter_url += '?' + '&'.join([f"{k}={v}" for k, v in filter_params.items() if v])

            return JsonResponse({
                'success': True,
                'found': len(vacancies_data),
                'saved': processed_count,
                'message': f'Найдено {len(vacancies_data)} вакансий, обработано {processed_count}',
                'filter_url': filter_url,
                'has_filters': has_active_filters and len(vacancies_data) > 0
            })

        except Exception as e:
            print(f"Ошибка в ParserView: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': f'Ошибка: {str(e)}'})


class FilterVacanciesView(View):
    """
    API представление для фильтрации вакансий через JSON API.

    Предоставляет REST API для фильтрации вакансий по различным критериям.
    Поддерживает сложную логику сопоставления фильтров с данными вакансий.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """Отключает CSRF защиту для API запросов."""
        return super().dispatch(*args, **kwargs)

    def post(self, request) -> JsonResponse:
        """
        Обработка POST-запросов для фильтрации вакансий через API.

        Args:
            request: HttpRequest (объект запроса с JSON данными фильтров)

        Returns:
            JsonResponse: отфильтрованный список вакансий в JSON формате
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

        Args:
            experience_code: str (код опыта работы)

        Returns:
            str: читаемое название уровня опыта
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

        Args:
            employment_code: str (код типа занятости)

        Returns:
            str: читаемое название типа занятости
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

        Выполняет комплексную проверку вакансии по всем критериям фильтрации.
        Поддерживает фильтры по зарплате, опыту, занятости и ключевым словам.

        Args:
            vacancy: Vacancy (объект вакансии для проверки)
            filters: dict (словарь с параметрами фильтрации)

        Returns:
            bool: True если вакансия соответствует всем фильтрам, иначе False
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

                # Проверяем наличие ключевых слов в любом из полей
                keyword_found = any(keywords in field for field in search_fields if field)
                if not keyword_found:
                    return False

        # Фильтр по минимальной зарплате
        if filters.get('min_salary'):
            try:
                min_salary = int(filters['min_salary'])
                salary_text = getattr(vacancy, 'salary', '')

                if salary_text and "Не указана" not in salary_text:
                    # Извлекаем числа из строки зарплаты
                    numbers = re.findall(r'\d+', salary_text.replace(' ', '').replace(',', ''))
                    if numbers:
                        # Берем максимальное число из найденных (для диапазонов "100-200")
                        salary_value = max(map(int, numbers))
                        if salary_value < min_salary:
                            return False
            except (ValueError, TypeError):
                # Если преобразование не удалось, пропускаем фильтр
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

        # Новый фильтр: минимальное количество лет опыта
        if filters.get('min_experience_years'):
            try:
                min_years = int(filters['min_experience_years'])
                vacancy_experience = getattr(vacancy, 'experience', '')
                experience_years = self.get_experience_years(vacancy_experience)

                if experience_years < min_years:
                    return False
            except (ValueError, TypeError):
                # Если преобразование не удалось, пропускаем фильтр
                pass

        return True

    def get_experience_years(self, experience_code: str) -> int:
        """
        Конвертирует код опыта в количество лет для численного сравнения.

        Args:
            experience_code: str (код опыта работы)

        Returns:
            int: количество лет опыта
        """
        experience_map = {
            'no': 0,
            '1-3': 2,  # среднее значение
            '3-6': 4,  # среднее значение
            '6+': 7  # минимальное значение для "более 6 лет"
        }
        return experience_map.get(experience_code, 0)


class GenerateLetterView(View):
    """
    API представление для генерации сопроводительных писем.

    Создает шаблоны сопроводительных писем на основе данных вакансии.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """Отключает CSRF защиту для API запросов."""
        return super().dispatch(*args, **kwargs)

    def post(self, request) -> JsonResponse:
        """
        Обработка POST-запросов для генерации сопроводительного письма.

        Args:
            request: HttpRequest (объект запроса с данными вакансии)

        Returns:
            JsonResponse: сгенерированное письмо в JSON формате
        """
        try:
            data = json.loads(request.body)
            vacancy_id = data.get('vacancy_id')
            template_type = data.get('template_type', 'standard')
            custom_text = data.get('custom_text', '')

            vacancy = Vacancy.objects.get(id=vacancy_id)

            # Простой генератор писем
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

        Args:
            request: HttpRequest (объект запроса)

        Returns:
            JsonResponse: список вакансий в JSON формате
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

    Предоставляет данные о количестве вакансий, распределении по опыту работы
    и типам занятости для аналитики и визуализации.
    """

    def get(self, request) -> JsonResponse:
        """
        Обработка GET-запросов для получения статистических данных.

        Args:
            request: HttpRequest (объект запроса)

        Returns:
            JsonResponse: JSON с статистикой вакансий
        """
        try:
            total_vacancies = Vacancy.objects.count()
            recent_count = Vacancy.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count()

            # Статистика по опыту работы
            experience_stats = {
                'no': Vacancy.objects.filter(experience='no').count(),
                '1-3': Vacancy.objects.filter(experience='1-3').count(),
                '3-6': Vacancy.objects.filter(experience='3-6').count(),
                '6+': Vacancy.objects.filter(experience='6+').count(),
            }

            # Статистика по типу занятости
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