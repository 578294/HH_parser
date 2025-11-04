class UniversalVacancyFilter:
    """Универсальный фильтр для всех стилей"""

    @staticmethod
    def filter_vacancies(vacancies, filters, style='default'):
        """
        Фильтрация вакансий с поддержкой всех стилей
        """
        filtered = []

        for vacancy in vacancies:
            if UniversalVacancyFilter._matches_filters(vacancy, filters, style):
                filtered.append(vacancy)

        return filtered

    @staticmethod
    def _matches_filters(vacancy, filters, style):
        """Проверка соответствия вакансии фильтрам"""

        # Фильтр по ключевым словам
        if filters.get('keywords'):
            keywords = filters['keywords'].lower()
            if not UniversalVacancyFilter._matches_keywords(vacancy, keywords, style):
                return False

        # Фильтр по минимальной зарплате
        if filters.get('min_salary'):
            min_salary = int(filters['min_salary'])
            if not UniversalVacancyFilter._matches_salary(vacancy, min_salary, style):
                return False

        # Фильтр по опыту
        if filters.get('experience') and filters['experience'] != 'any':
            if vacancy.experience != filters['experience']:
                return False

        # Фильтр по типу занятости
        if filters.get('employment') and filters['employment'] != 'any':
            if vacancy.employment != filters['employment']:
                return False

        return True

    @staticmethod
    def _matches_keywords(vacancy, keywords, style):
        """Проверка ключевых слов с учетом стиля"""
        search_fields = []

        # Добавляем поля для поиска в зависимости от стиля
        if style == 'HP':
            search_fields.extend([
                getattr(vacancy, 'hp_title', vacancy.title).lower(),
                getattr(vacancy, 'hp_company', vacancy.company).lower(),
                vacancy.description.lower(),
                getattr(vacancy, 'hp_salary', vacancy.salary).lower()
            ])
        elif style == 'SP':
            search_fields.extend([
                getattr(vacancy, 'sp_title', vacancy.title).lower(),
                getattr(vacancy, 'sp_company', vacancy.company).lower(),
                vacancy.description.lower(),
                getattr(vacancy, 'sp_salary', vacancy.salary).lower()
            ])
        elif style == 'WH':
            search_fields.extend([
                getattr(vacancy, 'wh_title', vacancy.title).lower(),
                getattr(vacancy, 'wh_company', vacancy.company).lower(),
                vacancy.description.lower(),
                getattr(vacancy, 'wh_salary', vacancy.salary).lower()
            ])
        else:
            search_fields.extend([
                vacancy.title.lower(),
                vacancy.company.lower(),
                vacancy.description.lower(),
                vacancy.salary.lower()
            ])

        # Проверяем наличие ключевых слов в любом из полей
        for field in search_fields:
            if keywords in field:
                return True
        return False

    @staticmethod
    def _matches_salary(vacancy, min_salary, style):
        """Проверка зарплаты с учетом стиля"""
        salary_text = ""

        if style == 'HP':
            salary_text = getattr(vacancy, 'hp_salary', vacancy.salary)
        elif style == 'SP':
            salary_text = getattr(vacancy, 'sp_salary', vacancy.salary)
        elif style == 'WH':
            salary_text = getattr(vacancy, 'wh_salary', vacancy.salary)
        else:
            salary_text = vacancy.salary

        # Извлекаем числа из текста зарплаты
        import re
        numbers = re.findall(r'\d+', salary_text)
        if numbers:
            # Берем максимальное число из найденных (для диапазонов "100-200")
            salary_value = max(map(int, numbers))
            return salary_value >= min_salary

        # Если зарплата не указана или не распознана, пропускаем фильтр
        return True


class StyleFilterManager:
    """Менеджер фильтров для разных стилей"""

    @staticmethod
    def get_filter_config(style):
        """Конфигурация фильтров для каждого стиля"""
        configs = {
            'default': {
                'experience_options': [
                    {'value': '', 'text': 'ЛЮБОЙ'},
                    {'value': 'no', 'text': 'Без опыта'},
                    {'value': '1-3', 'text': '1-3 года'},
                    {'value': '3-6', 'text': '3-6 лет'},
                    {'value': '6+', 'text': 'Более 6 лет'}
                ],
                'employment_options': [
                    {'value': '', 'text': 'ЛЮБОЙ'},
                    {'value': 'full', 'text': 'Полная занятость'},
                    {'value': 'part', 'text': 'Частичная занятость'},
                    {'value': 'remote', 'text': 'Удаленная работа'},
                    {'value': 'project', 'text': 'Проектная работа'}
                ],
                'salary_placeholder': 'Минимальная зарплата',
                'keywords_placeholder': 'Ключевые слова...'
            },
            'HP': {
                'experience_options': [
                    {'value': '', 'text': 'ЛЮБОЙ (ДАЖЕ МАГЛ!)'},
                    {'value': 'no', 'text': 'НЕОФИТ (ПЕРВОКУРСНИК)'},
                    {'value': '1-3', 'text': '1-3 ГОДА (СТАРШЕКУРСНИК)'},
                    {'value': '3-6', 'text': '3-6 ЛЕТ (ВЫПУСКНИК ХОГВАРТСА)'},
                    {'value': '6+', 'text': 'БОЛЕЕ 6 ЛЕТ (ПРОФЕССОР)'}
                ],
                'employment_options': [
                    {'value': '', 'text': 'ЛЮБАЯ (ДАЖЕ В МИНИСТЕРСТВЕ!)'},
                    {'value': 'full', 'text': 'ПОЛНАЯ (КАК У ДИРЕКТОРА)'},
                    {'value': 'part', 'text': 'ЧАСТИЧНАЯ (ПО СОВМЕСТИТЕЛЬСТВУ)'},
                    {'value': 'remote', 'text': 'УДАЛЕННАЯ (ЧЕРЕЗ КАМИН)'},
                    {'value': 'project', 'text': 'ПРОЕКТНАЯ (МИССИЯ)'}
                ],
                'salary_placeholder': 'МИНИМАЛЬНАЯ ЗАРПЛАТА (В ГАЛЕОНАХ)',
                'keywords_placeholder': 'ЗАКЛИНАНИЯ, ПРЕДМЕТЫ, НАВЫКИ...'
            },
            'SP': {
                'experience_options': [
                    {'value': '', 'text': 'ЛЮБОЙ (ДАЖЕ У КАРТМАНА!)'},
                    {'value': 'no', 'text': 'БЕЗ ОПЫТА (КАК КАРТМАН)'},
                    {'value': '1-3', 'text': '1-3 ГОДА (КАК КЕНИ В 4 КЛАССЕ)'},
                    {'value': '3-6', 'text': '3-6 ЛЕТ (КАК СТЭН ПОСЛЕ ШКОЛЫ)'},
                    {'value': '6+', 'text': 'БОЛЕЕ 6 ЛЕТ (КАК МИСТЕР ГАРРИСОН)'}
                ],
                'employment_options': [
                    {'value': '', 'text': 'ЛЮБАЯ (RESPECT MY AUTHORITAH!)'},
                    {'value': 'full', 'text': 'ПОЛНАЯ (КАК У ШЕФА)'},
                    {'value': 'part', 'text': 'ЧАСТИЧНАЯ (МЕЖДУ ИГРАМИ)'},
                    {'value': 'remote', 'text': 'УДАЛЕННАЯ (ИЗ ДОМА)'},
                    {'value': 'project', 'text': 'ПРОЕКТНАЯ (ПРИКЛЮЧЕНИЕ)'}
                ],
                'salary_placeholder': 'МИНИМАЛЬНАЯ ЗАРПЛАТА ($)',
                'keywords_placeholder': 'PYTHON, LINUX, CHEESY POOFS...'
            },
            'WH': {
                'experience_options': [
                    {'value': '', 'text': 'ЛЮБОЙ (ДАЖЕ У ЕРЕТИКА!)'},
                    {'value': 'no', 'text': 'НЕОФИТ (НОВОБРАНЕЦ)'},
                    {'value': '1-3', 'text': '1-3 ГОДА (ОПЫТНЫЙ ГВАРДИЕЦ)'},
                    {'value': '3-6', 'text': '3-6 ЛЕТ (ВЕТЕРАН КАДИИ)'},
                    {'value': '6+', 'text': 'БОЛЕЕ 6 ЛЕТ (СЕРЫЙ РЫЦАРЬ)'}
                ],
                'employment_options': [
                    {'value': '', 'text': 'ЛЮБАЯ (ЗА ИМПЕРАТОРА!)'},
                    {'value': 'full', 'text': 'ПОЛНАЯ (КРЕСТОВЫЙ ПОХОД)'},
                    {'value': 'part', 'text': 'ЧАСТИЧНАЯ (ПАТРУЛИРОВАНИЕ)'},
                    {'value': 'remote', 'text': 'ДИСТАНЦИОННАЯ (АСТРОПАТ)'},
                    {'value': 'project', 'text': 'ПРОЕКТНАЯ (ЭКСПЕДИЦИЯ)'}
                ],
                'salary_placeholder': 'МИНИМАЛЬНАЯ ДЕСЯТИНА (В ДУКАТАХ)',
                'keywords_placeholder': 'PYTHON, MACHINE SPIRIT, HERESY...'
            }
        }

        return configs.get(style, configs['default'])