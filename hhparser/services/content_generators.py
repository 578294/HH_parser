# hhparser/services/content_generators.py

class StyleContentGenerator:
    """Генератор стилизованного контента"""

    @staticmethod
    def style_vacancies(vacancies, style):
        """Преобразование вакансий в выбранный стиль"""
        styled_vacancies = []

        for vacancy in vacancies:
            if style == 'HP':
                styled_vacancies.append({
                    'id': vacancy.id,
                    'title': vacancy.get_hp_title(),
                    'company': vacancy.get_hp_company(),
                    'salary': vacancy.get_hp_salary(),
                    'experience': StyleContentGenerator.generate_experience_text(vacancy.experience, 'HP'),
                    'employment': StyleContentGenerator.generate_employment_text(vacancy.employment, 'HP'),
                    'description': vacancy.description,
                    'link': vacancy.link,
                    'created_at': vacancy.created_at
                })
            elif style == 'SP':
                styled_vacancies.append({
                    'id': vacancy.id,
                    'title': vacancy.get_sp_title(),
                    'company': vacancy.get_sp_company(),
                    'salary': vacancy.get_sp_salary(),
                    'experience': StyleContentGenerator.generate_experience_text(vacancy.experience, 'SP'),
                    'employment': StyleContentGenerator.generate_employment_text(vacancy.employment, 'SP'),
                    'description': vacancy.description,
                    'link': vacancy.link,
                    'created_at': vacancy.created_at
                })
            elif style == 'WH':
                styled_vacancies.append({
                    'id': vacancy.id,
                    'title': vacancy.get_wh_title(),
                    'company': vacancy.get_wh_company(),
                    'salary': vacancy.get_wh_salary(),
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

        return styled_vacancies

    @staticmethod
    def generate_experience_text(experience_code, style):
        """Генерация текста опыта для разных стилей"""
        experiences = {
            'default': {
                'no': 'Без опыта',
                '1-3': '1-3 года',
                '3-6': '3-6 лет',
                '6+': 'Более 6 лет'
            },
            'HP': {
                'no': 'НЕОФИТ (КАК ПЕРВОКУРСНИК)',
                '1-3': '1-3 ГОДА (СТАРШЕКУРСНИК)',
                '3-6': '3-6 ЛЕТ (ВЫПУСКНИК ХОГВАРТСА)',
                '6+': 'БОЛЕЕ 6 ЛЕТ (ПРОФЕССОР)'
            },
            'SP': {
                'no': 'БЕЗ ОПЫТА (КАК КАРТМАН)',
                '1-3': '1-3 ГОДА (КАК КЕНИ В 4 КЛАССЕ)',
                '3-6': '3-6 ЛЕТ (КАК СТЭН ПОСЛЕ ШКОЛЫ)',
                '6+': 'БОЛЕЕ 6 ЛЕТ (КАК МИСТЕР ГАРРИСОН)'
            },
            'WH': {
                'no': 'НЕОФИТ (НОВОБРАНЕЦ)',
                '1-3': '1-3 ГОДА (ОПЫТНЫЙ ГВАРДИЕЦ)',
                '3-6': '3-6 ЛЕТ (ВЕТЕРАН КАДИИ)',
                '6+': 'БОЛЕЕ 6 ЛЕТ (СЕРЫЙ РЫЦАРЬ)'
            }
        }
        return experiences.get(style, experiences['default']).get(experience_code, 'Неизвестно')

    @staticmethod
    def generate_employment_text(employment_code, style):
        """Генерация текста занятости для разных стилей"""
        employments = {
            'default': {
                'full': 'Полная занятость',
                'part': 'Частичная занятость',
                'remote': 'Удаленная работа',
                'project': 'Проектная работа'
            },
            'HP': {
                'full': 'ПОЛНАЯ (КАК У ДИРЕКТОРА)',
                'part': 'ЧАСТИЧНАЯ (ПО СОВМЕСТИТЕЛЬСТВУ)',
                'remote': 'УДАЛЕННАЯ (ЧЕРЕЗ КАМИН)',
                'project': 'ПРОЕКТНАЯ (МИССИЯ)'
            },
            'SP': {
                'full': 'ПОЛНАЯ (КАК У ШЕФА)',
                'part': 'ЧАСТИЧНАЯ (МЕЖДУ ИГРАМИ)',
                'remote': 'УДАЛЕННАЯ (ИЗ ДОМА)',
                'project': 'ПРОЕКТНАЯ (ПРИКЛЮЧЕНИЕ)'
            },
            'WH': {
                'full': 'ПОЛНАЯ (КРЕСТОВЫЙ ПОХОД)',
                'part': 'ЧАСТИЧНАЯ (ПАТРУЛИРОВАНИЕ)',
                'remote': 'ДИСТАНЦИОННАЯ (АСТРОПАТ)',
                'project': 'ПРОЕКТНАЯ (ЭКСПЕДИЦИЯ)'
            }
        }
        return employments.get(style, employments['default']).get(employment_code, 'Неизвестно')