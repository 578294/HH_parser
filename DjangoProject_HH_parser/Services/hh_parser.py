import requests
import time
from django.utils import timezone
from hhparser.models import Vacancy

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 YaBrowser/25.6.0.0 Safari/537.36"

class HHApiParser:
    def __init__(self):
        self.base_url = "https://api.hh.ru/vacancies"
        self.session = requests.Session()
        self.session.headers.update({'user-agent':USER_AGENT})

    def parse_vacancies(self, search_query="python", pages=1):
        """Основной метод парсинга вакансий"""
        all_vacancies = []

        for page in range(pages):
            print(f"Парсинг страницы {page + 1}")

            params = {
                'text': search_query,
                'page': page,
                'per_page': 50,
                'area': 1,  # Москва
            }

            try:
                response = self.session.get(self.base_url, params=params, timeout=10)
                data = response.json()

                if 'items' not in data:
                    break

                for vacancy_data in data['items']:
                    try:
                        vacancy = self.parse_vacancy_item(vacancy_data)
                        if vacancy:
                            all_vacancies.append(vacancy)
                    except Exception as e:
                        print(f"Ошибка парсинга вакансии: {e}")
                        continue

                time.sleep(1)

            except Exception as e:
                print(f"Ошибка запроса: {e}")
                continue

        return all_vacancies

    def parse_vacancy_item(self, vacancy_data):
        """Парсинг отдельной вакансии"""
        # Опыт работы (маппинг API -> нашу модель)
        experience_map = {
            'noExperience': 'no',
            'between1And3': '1-3',
            'between3And6': '3-6',
            'moreThan6': '6+'
        }

        # Тип занятости
        employment_map = {
            'full': 'full',
            'part': 'part',
            'remote': 'remote',
            'project': 'project'
        }

        experience = experience_map.get(vacancy_data.get('experience', {}).get('id'), 'no')
        employment = employment_map.get(vacancy_data.get('employment', {}).get('id'), 'full')

        vacancy_info = {
            'title': vacancy_data.get('name', ''),
            'company': vacancy_data.get('employer', {}).get('name', ''),
            'salary': self.parse_salary(vacancy_data.get('salary')),
            'description': self.clean_description(vacancy_data.get('snippet', {})),
            'experience': experience,
            'employment': employment,
            'skills': ', '.join([skill['name'] for skill in vacancy_data.get('key_skills', [])]),
            'link': vacancy_data.get('alternate_url', ''),
        }

        return vacancy_info

    def parse_salary(self, salary_data):
        """Обработка зарплаты"""
        if not salary_data:
            return "Не указана"

        salary_from = salary_data.get('from')
        salary_to = salary_data.get('to')
        currency = '₽' if salary_data.get('currency') == 'RUR' else salary_data.get('currency', '')

        if salary_from and salary_to:
            return f"{salary_from} - {salary_to} {currency}"
        elif salary_from:
            return f"от {salary_from} {currency}"
        elif salary_to:
            return f"до {salary_to} {currency}"
        else:
            return "Не указана"

    def clean_description(self, snippet):
        """Очистка описания"""
        requirement = snippet.get('requirement', '')
        responsibility = snippet.get('responsibility', '')

        description = f"{requirement} {responsibility}".strip()
        return description[:1000]  # Ограничиваем длину

    def save_to_database(self, vacancies):
        """Сохранение вакансий в базу данных"""
        saved_count = 0

        for vacancy_info in vacancies:
            try:
                obj, created = Vacancy.objects.update_or_create(
                    link=vacancy_info['link'],
                    defaults={**vacancy_info}
                )
                if created:
                    saved_count += 1
                    print(f"Сохранена вакансия: {vacancy_info['title']}")
            except Exception as e:
                print(f"Ошибка сохранения вакансии: {e}")
                continue

        return saved_count






