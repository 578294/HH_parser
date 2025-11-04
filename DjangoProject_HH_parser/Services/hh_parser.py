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

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 YaBrowser/25.6.0.0 Safari/537.36"


class HHApiParser:
    def __init__(self):
        self.base_url = "https://api.hh.ru/vacancies"
        self.session = requests.Session()
        self.session.headers.update({'user-agent': USER_AGENT, 'HH-User-Agent': 'HH Parser App'})

    def parse_vacancies(self, search_query="Python", vacancy_count=50):
        all_vacancies = []
        page = 0
        per_page = min(50, vacancy_count)  # Максимум 50 вакансий на страницу

        # Ограничиваем максимальное количество вакансий для избежания лимитов API
        if vacancy_count > 500:
            vacancy_count = 500

        while len(all_vacancies) < vacancy_count:
            print(f"Парсинг страницы {page + 1}, собрано {len(all_vacancies)}/{vacancy_count} вакансий")

            params = {
                'text': search_query,
                'page': page,
                'per_page': per_page,
                'area': 1,  # Москва
                'only_with_salary': False,
            }

            try:
                response = self.session.get(self.base_url, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()

                if 'items' not in data or not data['items']:
                    print(f"На странице {page + 1} нет вакансий")
                    break

                for vacancy_data in data['items']:
                    if len(all_vacancies) >= vacancy_count:
                        break

                    try:
                        vacancy = self.parse_vacancy_item(vacancy_data)
                        if vacancy:
                            all_vacancies.append(vacancy)
                    except Exception as e:
                        print(f"Ошибка парсинга вакансии: {e}")
                        continue

                # Проверяем, есть ли еще страницы
                if page >= data['pages'] - 1:
                    print("Достигнут конец списка вакансий")
                    break

                page += 1
                time.sleep(0.5)  # Уважаем API HH.ru

            except requests.exceptions.RequestException as e:
                print(f"Ошибка сети при запросе: {e}")
                break
            except Exception as e:
                print(f"Общая ошибка: {e}")
                continue

        print(f"Всего собрано вакансий: {len(all_vacancies)}")
        return all_vacancies

    def parse_vacancy_item(self, vacancy_data):
        """Парсинг отдельной вакансии с улучшенной обработкой данных"""

        # Проверяем наличие обязательных данных
        if not vacancy_data.get('name') or not vacancy_data.get('alternate_url'):
            print(f"❌ Пропуск вакансии: отсутствуют обязательные данные")
            return None

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

        # Обрабатываем навыки
        skills_text = ', '.join([skill['name'] for skill in vacancy_data.get('key_skills', [])])
        if len(skills_text) > 1000:  # Ограничиваем длину
            skills_text = skills_text[:1000] + "..."

        vacancy_info = {
            'title': vacancy_data.get('name', 'Без названия').strip(),
            'company': vacancy_data.get('employer', {}).get('name', 'Не указано').strip(),
            'salary': self.parse_salary(vacancy_data.get('salary')),
            'description': description,
            'experience': experience,
            'employment': employment,
            'skills': skills_text,
            'link': vacancy_data.get('alternate_url', '').strip(),
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
            return clean_description[:1500]  # Ограничиваем длину

        except Exception as e:
            print(f"Не удалось получить полное описание: {e}")
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
        updated_count = 0
        skipped_count = 0

        for vacancy_info in vacancies:
            try:
                # Проверяем обязательные поля
                if not vacancy_info.get('title'):
                    print(f"❌ Пропуск: отсутствует название")
                    skipped_count += 1
                    continue

                if not vacancy_info.get('link'):
                    print(f"❌ Пропуск '{vacancy_info.get('title', '')}': отсутствует ссылка")
                    skipped_count += 1
                    continue

                # Проверяем корректность ссылки
                if not vacancy_info['link'].startswith('http'):
                    print(f"❌ Пропуск '{vacancy_info['title']}': некорректная ссылка '{vacancy_info['link']}'")
                    skipped_count += 1
                    continue

                # Подготавливаем данные
                vacancy_data = {
                    'title': vacancy_info.get('title', '').strip(),
                    'company': vacancy_info.get('company', '').strip(),
                    'salary': vacancy_info.get('salary', 'Не указана'),
                    'description': vacancy_info.get('description', ''),
                    'experience': vacancy_info.get('experience', 'no'),
                    'employment': vacancy_info.get('employment', 'full'),
                    'skills': vacancy_info.get('skills', ''),
                }

                # Сохраняем или обновляем
                obj, created = Vacancy.objects.update_or_create(
                    link=vacancy_info['link'].strip(),
                    defaults=vacancy_data
                )

                if created:
                    saved_count += 1
                    print(f"✅ Сохранена: {vacancy_info['title'][:60]}...")
                else:
                    updated_count += 1
                    print(f"🔄 Обновлена: {vacancy_info['title'][:60]}...")

            except Exception as e:
                print(f"❌ Ошибка сохранения '{vacancy_info.get('title', 'Без названия')}': {e}")
                skipped_count += 1
                continue

        print(f"📊 Итог: сохранено {saved_count}, обновлено {updated_count}, пропущено {skipped_count}")
        total_processed = saved_count + updated_count
        return total_processed