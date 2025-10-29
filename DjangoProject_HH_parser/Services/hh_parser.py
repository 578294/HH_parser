import requests
import time
import os
import django
import sys
from django.utils import timezone
from hhparser.models import Vacancy

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject_HH_parser.settings')
django.setup()


class HHApiParser:
    def __init__(self):
        self.base_url = "https://api.hh.ru/vacancies"
        self.session = requests.Session()
        self.session.headers.update({
            'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            'HH-User-Agent': 'HH Parser App'
        })

    def parse_vacancies(self, search_query="Python", pages=1):
        all_vacancies = []

        for page in range(min(pages, 10)):  # Ограничение 10 страниц
            print(f"Парсинг страницы {page + 1} из {pages}")

            params = {
                'text': search_query,
                'page': page,
                'per_page': 50,
                'area': 1,  # Москва
                'only_with_salary': False,
            }

            try:
                response = self.session.get(self.base_url, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()

                if 'items' not in data or not data['items']:
                    break

                for vacancy_data in data['items']:
                    try:
                        vacancy = self.parse_vacancy_item(vacancy_data)
                        if vacancy:
                            all_vacancies.append(vacancy)
                    except Exception as e:
                        print(f"Ошибка парсинга вакансии: {e}")
                        continue

                if page >= data['pages'] - 1:
                    break

                time.sleep(0.5)

            except Exception as e:
                print(f"Ошибка: {e}")
                continue

        print(f"Всего собрано вакансий: {len(all_vacancies)}")
        return all_vacancies

    def parse_vacancy_item(self, vacancy_data):
        """Парсинг вакансии с генерацией стилизованных данных"""
        experience_map = {
            'noExperience': 'no',
            'between1And3': '1-3',
            'between3And6': '3-6',
            'moreThan6': '6+'
        }

        employment_map = {
            'full': 'full',
            'part': 'part',
            'remote': 'remote',
            'project': 'project'
        }

        experience = experience_map.get(vacancy_data.get('experience', {}).get('id'), 'no')
        employment = employment_map.get(vacancy_data.get('employment', {}).get('id'), 'full')
        description = self.get_full_description(vacancy_data.get('url'))

        # Создаем временный объект для генерации стилизованных данных
        temp_vacancy = Vacancy(
            title=vacancy_data.get('name', 'Без названия'),
            company=vacancy_data.get('employer', {}).get('name', 'Не указано'),
            salary=self.parse_salary(vacancy_data.get('salary')),
            description=description,
            experience=experience,
            employment=employment,
            skills=', '.join([skill['name'] for skill in vacancy_data.get('key_skills', [])]),
            link=vacancy_data.get('alternate_url', ''),
        )

        # Генерируем стилизованные данные
        vacancy_info = {
            'title': temp_vacancy.title,
            'company': temp_vacancy.company,
            'salary': temp_vacancy.salary,
            'description': temp_vacancy.description,
            'experience': temp_vacancy.experience,
            'employment': temp_vacancy.employment,
            'skills': temp_vacancy.skills,
            'link': temp_vacancy.link,
            # Стилизованные данные
            'hp_title': temp_vacancy.generate_hp_title(),
            'hp_company': temp_vacancy.company.upper() + " (ОТДЕЛ МАГИИ)",
            'hp_salary': temp_vacancy.generate_hp_salary(),

            'sp_title': temp_vacancy.generate_sp_title(),
            'sp_company': temp_vacancy.company.upper() + " (СЕРЬЕЗНО!)",
            'sp_salary': temp_vacancy.generate_sp_salary(),

            'wh_title': temp_vacancy.generate_wh_title(),
            'wh_company': temp_vacancy.company.upper() + " ИМПЕРИУМ",
            'wh_salary': temp_vacancy.generate_wh_salary(),
        }

        return vacancy_info

    def get_full_description(self, vacancy_url):
        """Получение полного описания вакансии"""
        if not vacancy_url:
            return ""

        try:
            response = self.session.get(vacancy_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            description = data.get('description', '')
            import re
            clean_description = re.sub('<[^<]+?>', '', description)
            return clean_description[:1500]
        except:
            return ""

    def parse_salary(self, salary_data):
        """Обработка зарплаты"""
        if not salary_data:
            return "Не указана"

        salary_from = salary_data.get('from')
        salary_to = salary_data.get('to')
        currency = '₽' if salary_data.get('currency') == 'RUR' else salary_data.get('currency', '')

        if salary_from and salary_to:
            return f"{salary_from:,} - {salary_to:,} {currency}".replace(',', ' ')
        elif salary_from:
            return f"от {salary_from:,} {currency}".replace(',', ' ')
        elif salary_to:
            return f"до {salary_to:,} {currency}".replace(',', ' ')
        else:
            return "Не указана"

    def save_to_database(self, vacancies):
        saved_count = 0

        for vacancy_info in vacancies:
            try:
                if not vacancy_info.get('title') or not vacancy_info.get('link'):
                    continue

                obj, created = Vacancy.objects.update_or_create(
                    link=vacancy_info['link'],
                    defaults={**vacancy_info}
                )
                if created:
                    saved_count += 1
            except Exception as e:
                print(f"Ошибка сохранения: {e}")
                continue

        return saved_count