# hhparser/views.py
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.utils import timezone
from .models import Vacancy
from DjangoProject_HH_parser.Services.hh_parser import HHApiParser
import json


class VacancyListView(View):
    def get(self, request):
        search_query = request.GET.get('search', '')
        keywords = request.GET.get('keywords', '')
        min_salary = request.GET.get('min_salary', '')
        experience = request.GET.get('experience', '')
        employment = request.GET.get('employment', '')
        min_experience_years = request.GET.get('min_experience_years', '')

        vacancies = Vacancy.objects.all().order_by('-created_at')

        # Применяем поиск по ключевым словам
        if search_query:
            vacancies = vacancies.filter(
                Q(title__icontains=search_query) |
                Q(company__icontains=search_query) |
                Q(skills__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Применяем дополнительные фильтры через FilterVacanciesView
        filter_view = FilterVacanciesView()
        filtered_vacancies = []

        filters_dict = {
            'keywords': keywords,
            'min_salary': min_salary,
            'experience': experience,
            'employment': employment,
            'min_experience_years': min_experience_years,
        }

        # Если есть хотя бы один активный фильтр (кроме основного поиска)
        has_active_filters = any([
            keywords,
            min_salary,
            experience and experience != '',
            employment and employment != '',
            min_experience_years
        ])

        if has_active_filters:
            for vacancy in vacancies:
                if filter_view.matches_filters(vacancy, filters_dict):
                    filtered_vacancies.append(vacancy)

            # Преобразуем обратно в QuerySet для сохранения порядка
            vacancy_ids = [v.id for v in filtered_vacancies]
            vacancies = Vacancy.objects.filter(id__in=vacancy_ids).order_by('-created_at')
        else:
            filtered_vacancies = list(vacancies)

        return render(request, 'parser/html/vacancies.html', {
            'vacancies': vacancies,
            'search_query': search_query,
            'keywords': keywords,
            'min_salary': min_salary,
            'experience': experience,
            'employment': employment,
            'min_experience_years': min_experience_years,
            'vacancies_count': vacancies.count(),
            'current_filters': request.GET.dict(),
            'has_active_filters': has_active_filters
        })


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
        total_vacancies = Vacancy.objects.count()
        return render(request, 'parser/html/parser.html', {
            'total_vacancies': total_vacancies
        })

    def post(self, request):
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

            # Фильтруем None значения (если какие-то вакансии не распарсились)
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

            filter_url = '/vacancies/'
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
                        'created_at': vacancy.created_at.strftime('%d.%m.%Y %H:%M')
                    })

            return JsonResponse({
                'success': True,
                'vacancies': filtered_vacancies,
                'count': len(filtered_vacancies)
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def matches_filters(self, vacancy, filters):
        """Проверка фильтров с учетом опыта работы"""
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
                    import re
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

    def get_experience_years(self, experience_code):
        """Конвертирует код опыта в количество лет"""
        experience_map = {
            'no': 0,
            '1-3': 2,  # среднее значение
            '3-6': 4,  # среднее значение
            '6+': 7  # минимальное значение для "более 6 лет"
        }
        return experience_map.get(experience_code, 0)


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
    def get(self, request):
        try:
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
                    'created_at': vacancy.created_at.strftime('%d.%m.%Y %H:%M')
                })

            return JsonResponse({'vacancies': vacancy_list})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class StatisticsView(View):
    def get(self, request):
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