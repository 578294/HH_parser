"""
Модуль filters.py содержит классы для фильтрации вакансий.

Основные классы:
- UniversalVacancyFilter: универсальный фильтр для вакансий
- StyleFilterManager: менеджер конфигураций фильтров
"""

class UniversalVacancyFilter:
    """
    Универсальный фильтр для вакансий.

    Обеспечивает фильтрацию вакансий по ключевым словам, зарплате, опыту работы
    и типу занятости.
    """

    @staticmethod
    def filter_vacancies(vacancies: list, filters: dict) -> list:
        """
        Фильтрация списка вакансий по заданным параметрам.

        Применяет заданные фильтры к списку вакансий. Поддерживает все основные типы фильтров.

        Args:
            vacancies: list (список объектов вакансий для фильтрации)
            filters: dict (словарь с параметрами фильтрации)

        Returns:
            list: отфильтрованный список вакансий
        """
        filtered = []

        for vacancy in vacancies:
            if UniversalVacancyFilter._matches_filters(vacancy, filters):
                filtered.append(vacancy)

        return filtered

    @staticmethod
    def _matches_filters(vacancy: object, filters: dict) -> bool:
        """
        Проверяет соответствие вакансии заданным фильтрам.

        Выполняет комплексную проверку вакансии по всем критериям фильтрации.

        Args:
            vacancy: object (объект вакансии для проверки)
            filters: dict (словарь с параметрами фильтрации)

        Returns:
            bool: True если вакансия соответствует всем фильтрам, иначе False
        """
        # Фильтр по ключевым словам
        if filters.get('keywords'):
            keywords = filters['keywords'].lower()
            if not UniversalVacancyFilter._matches_keywords(vacancy, keywords):
                return False

        # Фильтр по минимальной зарплате
        if filters.get('min_salary'):
            min_salary = int(filters['min_salary'])
            if not UniversalVacancyFilter._matches_salary(vacancy, min_salary):
                return False

        # Фильтр по опыту работы
        if filters.get('experience') and filters['experience'] != 'any':
            if vacancy.experience != filters['experience']:
                return False

        # Фильтр по типу занятости
        if filters.get('employment') and filters['employment'] != 'any':
            if vacancy.employment != filters['employment']:
                return False

        return True

    @staticmethod
    def _matches_keywords(vacancy: object, keywords: str) -> bool:
        """
        Проверяет наличие ключевых слов в данных вакансии.

        Осуществляет поиск ключевых слов в различных полях вакансии.

        Args:
            vacancy: object (объект вакансии для поиска)
            keywords: str (ключевые слова для поиска в нижнем регистре)

        Returns:
            bool: True если ключевые слова найдены, иначе False
        """
        search_fields = [
            vacancy.title.lower(),
            vacancy.company.lower(),
            vacancy.description.lower(),
            vacancy.salary.lower()
        ]

        # Проверяем наличие ключевых слов в любом из полей
        for field in search_fields:
            if keywords in field:
                return True
        return False

    @staticmethod
    def _matches_salary(vacancy: object, min_salary: int) -> bool:
        """
        Проверяет соответствие зарплаты вакансии минимальному требованию.

        Анализирует данные о зарплате вакансии, извлекая числовые значения
        из текстового представления.

        Args:
            vacancy: object (объект вакансии для проверки)
            min_salary: int (минимальная требуемая зарплата)

        Returns:
            bool: True если зарплата соответствует требованию или не указана, иначе False
        """
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
    """
    Менеджер конфигураций фильтров.

    Предоставляет настройки интерфейса фильтрации.
    """

    @staticmethod
    def get_filter_config() -> dict:
        """
        Возвращает конфигурацию фильтров.

        Предоставляет тексты, плейсхолдеры и опции для элементов интерфейса фильтрации.

        Returns:
            dict: конфигурация фильтров
        """
        return {
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
        }