from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from .models import Vacancy, CoverLetter
from DjangoProject_HH_parser.Services.hh_parser import HHApiParser
from .services.content_generators import StyleContentGenerator, LetterTemplateGenerator
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
        style = request.GET.get('style', 'default')

        if search_query:
            vacancies = Vacancy.objects.filter(
                Q(title__icontains=search_query) |
                Q(company__icontains=search_query) |
                Q(skills__icontains=search_query)
            ).order_by('-created_at')
        else:
            vacancies = Vacancy.objects.all().order_by('-created_at')

        # Подготавливаем данные в выбранном стиле
        styled_vacancies = []
        for vacancy in vacancies:
            if style == 'HP':
                styled_vacancies.append({
                    'id': vacancy.id,
                    'title': vacancy.hp_title,
                    'company': vacancy.hp_company,
                    'salary': vacancy.hp_salary,
                    'experience': StyleContentGenerator.generate_experience_text(vacancy.experience, 'HP'),
                    'employment': StyleContentGenerator.generate_employment_text(vacancy.employment, 'HP'),
                    'description': vacancy.description,
                    'link': vacancy.link,
                    'created_at': vacancy.created_at
                })
            elif style == 'SP':
                styled_vacancies.append({
                    'id': vacancy.id,
                    'title': vacancy.sp_title,
                    'company': vacancy.sp_company,
                    'salary': vacancy.sp_salary,
                    'experience': StyleContentGenerator.generate_experience_text(vacancy.experience, 'SP'),
                    'employment': StyleContentGenerator.generate_employment_text(vacancy.employment, 'SP'),
                    'description': vacancy.description,
                    'link': vacancy.link,
                    'created_at': vacancy.created_at
                })
            elif style == 'WH':
                styled_vacancies.append({
                    'id': vacancy.id,
                    'title': vacancy.wh_title,
                    'company': vacancy.wh_company,
                    'salary': vacancy.wh_salary,
                    'experience': StyleContentGenerator.generate_experience_text(vacancy.experience, 'WH'),
                    'employment': StyleContentGenerator.generate_employment_text(vacancy.employment, 'WH'),
                    'description': vacancy.description,
                    'link': vacancy.link,
                    'created_at': vacancy.created_at
                })
            else:
                styled_vacancies.append({
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

        return render(request, 'parser/html/vacancies.html', {
            'vacancies': styled_vacancies,
            'search_query': search_query,
            'vacancies_count': len(styled_vacancies),
            'current_style': style
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

        # Подготавливаем данные в выбранном стиле
        styled_vacancies = []
        for vacancy in vacancies:
            if style == 'HP':
                styled_vacancies.append({
                    'id': vacancy.id,
                    'title': vacancy.hp_title,
                    'company': vacancy.hp_company,
                    'salary': vacancy.hp_salary,
                })
            elif style == 'SP':
                styled_vacancies.append({
                    'id': vacancy.id,
                    'title': vacancy.sp_title,
                    'company': vacancy.sp_company,
                    'salary': vacancy.sp_salary,
                })
            elif style == 'WH':
                styled_vacancies.append({
                    'id': vacancy.id,
                    'title': vacancy.wh_title,
                    'company': vacancy.wh_company,
                    'salary': vacancy.wh_salary,
                })
            else:
                styled_vacancies.append(vacancy)

        return render(request, template_name, {
            'vacancies': styled_vacancies,
            'current_style': style,
            'total_vacancies': Vacancy.objects.count()
        })


class GenerateLetterView(View):
    """Генерация сопроводительного письма"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        try:
            data = json.loads(request.body)
            vacancy_id = data.get('vacancy_id')
            template_type = data.get('template_type', 'standard')
            style = data.get('style', 'default')
            custom_text = data.get('custom_text', '')

            vacancy = Vacancy.objects.get(id=vacancy_id)
            letter_content = LetterTemplateGenerator.generate_letter(
                vacancy, template_type, style, custom_text
            )

            # Сохраняем письмо в базу
            cover_letter = CoverLetter.objects.create(
                title=f"Письмо для {vacancy.title}",
                content=letter_content,
                template_type=template_type,
                style=style,
                vacancy=vacancy
            )

            return JsonResponse({
                'success': True,
                'letter_content': letter_content,
                'letter_id': cover_letter.id
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class GetVacanciesView(View):
    """API для получения вакансий в определенном стиле"""

    def get(self, request):
        style = request.GET.get('style', 'default')
        vacancies = Vacancy.objects.all().order_by('-created_at')[:50]

        styled_vacancies = []
        for vacancy in vacancies:
            if style == 'HP':
                styled_vacancies.append({
                    'id': vacancy.id,
                    'title': vacancy.hp_title,
                    'company': vacancy.hp_company,
                    'salary': vacancy.hp_salary,
                    'experience': StyleContentGenerator.generate_experience_text(vacancy.experience, 'HP'),
                    'employment': StyleContentGenerator.generate_employment_text(vacancy.employment, 'HP'),
                })
            elif style == 'SP':
                styled_vacancies.append({
                    'id': vacancy.id,
                    'title': vacancy.sp_title,
                    'company': vacancy.sp_company,
                    'salary': vacancy.sp_salary,
                    'experience': StyleContentGenerator.generate_experience_text(vacancy.experience, 'SP'),
                    'employment': StyleContentGenerator.generate_employment_text(vacancy.employment, 'SP'),
                })
            elif style == 'WH':
                styled_vacancies.append({
                    'id': vacancy.id,
                    'title': vacancy.wh_title,
                    'company': vacancy.wh_company,
                    'salary': vacancy.wh_salary,
                    'experience': StyleContentGenerator.generate_experience_text(vacancy.experience, 'WH'),
                    'employment': StyleContentGenerator.generate_employment_text(vacancy.employment, 'WH'),
                })
            else:
                styled_vacancies.append({
                    'id': vacancy.id,
                    'title': vacancy.title,
                    'company': vacancy.company,
                    'salary': vacancy.salary,
                    'experience': vacancy.get_experience_display(),
                    'employment': vacancy.get_employment_display(),
                })

        return JsonResponse({
            'vacancies': styled_vacancies,
            'style': style
        })