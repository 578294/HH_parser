class StyleContentGenerator:
    """Базовый класс для генерации стилизованного контента"""

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


class LetterTemplateGenerator:
    """Генератор шаблонов писем для разных стилей"""

    @staticmethod
    def generate_letter(vacancy, template_type, style, custom_text=""):
        """Генерация письма в выбранном стиле"""

        if style == 'HP':
            return LetterTemplateGenerator._generate_hp_letter(vacancy, template_type, custom_text)
        elif style == 'SP':
            return LetterTemplateGenerator._generate_sp_letter(vacancy, template_type, custom_text)
        elif style == 'WH':
            return LetterTemplateGenerator._generate_wh_letter(vacancy, template_type, custom_text)
        else:
            return LetterTemplateGenerator._generate_default_letter(vacancy, template_type, custom_text)

    @staticmethod
    def _generate_hp_letter(vacancy, template_type, custom_text):
        base_letter = f"УВАЖАЕМЫЕ ВОЛШЕБНИКИ ИЗ {vacancy.company.upper()}!\n\n"
        base_letter += f"Я ПИШУ ПО ПОВОДУ ВАКАНСИИ '{vacancy.hp_title}'.\n\n"

        if template_type == 'support':
            base_letter += "КАК ВЕРНАЯ ПОМОЩНИЦА ГЕРМИОНЫ, Я ВНИМАТЕЛЬНА К ДЕТАЛЯМ...\n\n"
        elif template_type == 'devops':
            base_letter += "МОИ ЗАКЛИНАНИЯ DOCKER И KUBERNETES НЕУЛОЖИМЫ...\n\n"
        else:
            base_letter += "МОЙ МАГИЧЕСКИЙ ОПЫТ И НАВЫКИ СООТВЕТСТВУЮТ ВАШИМ ТРЕБОВАНИЯМ...\n\n"

        base_letter += "С УВАЖЕНИЕМ,\nВАШ ПОСЛУШНИК ИЗ ХОГВАРТСА"

        if custom_text:
            base_letter += f"\n\nP.S. {custom_text.upper()}"

        return base_letter

    @staticmethod
    def _generate_sp_letter(vacancy, template_type, custom_text):
        base_letter = f"ЭЙ, РЕБЯТА ИЗ {vacancy.company.upper()}!\n\n"
        base_letter += f"Я ХОЧУ РАБОТАТЬ У ВАС НА РОЛИ '{vacancy.sp_title}'.\n\n"

        if template_type == 'support':
            base_letter += "Я КАК КАРТМАН - СДЕЛАЮ ВСЕ, ЧТОБЫ ВЫ БЫЛИ ДОВОЛЬНЫ (ЕСЛИ КУПИТЕ CHEESY POOFS)...\n\n"
        elif template_type == 'devops':
            base_letter += "МОЙ ОПЫТ - КАК У КЕНИ, ТОЛЬКО БЕЗ СМЕРТЕЙ...\n\n"
        else:
            base_letter += "Я СЕРЬЕЗНО ХОРОШ В ЭТОМ, СПРОСИТЕ У МАМЫ...\n\n"

        base_letter += "С УВАЖЕНИЕМ,\nВАШ БУДУЩИЙ СОТРУДНИК"

        if custom_text:
            base_letter += f"\n\nP.S. {custom_text.upper()}"

        return base_letter

    @staticmethod
    def _generate_wh_letter(vacancy, template_type, custom_text):
        base_letter = f"ВЕЛИКОМУ {vacancy.company.upper()}!\n\n"
        base_letter += f"Я, СМИРЕННЫЙ СЛУГА ИМПЕРИУМА, ПИШУ О ВАКАНСИИ '{vacancy.wh_title}'.\n\n"

        if template_type == 'support':
            base_letter += "КАК ВЕРНЫЙ АДЕПТУС МЕХАНИКУС, Я ОБСЛУЖИВАЮ МАШИННЫЙ ДУХ...\n\n"
        elif template_type == 'devops':
            base_letter += "МОИ РИТУАЛЫ DOCKER И KUBERNETES УСМИРЯТ ЛЮБОГО МАШИННОГО ДУХА...\n\n"
        else:
            base_letter += "МОЙ ОПЫТ СЛУЖЕНИЯ СООТВЕТСТВУЕТ ВАШИМ ТРЕБОВАНИЯМ...\n\n"

        base_letter += "С ВЕРНОСТЬЮ ИМПЕРАТОРУ,\nВАШ ПОСЛУШНИК"

        if custom_text:
            base_letter += f"\n\nP.S. {custom_text.upper()}"

        return base_letter

    @staticmethod
    def _generate_default_letter(vacancy, template_type, custom_text):
        # Стандартный шаблон письма
        base_letter = f"Уважаемые представители {vacancy.company}!\n\n"
        base_letter += f"Я пишу по поводу вакансии '{vacancy.title}'.\n\n"

        if template_type == 'support':
            base_letter += "Мой опыт работы в технической поддержке...\n\n"
        elif template_type == 'devops':
            base_letter += "Мой опыт в DevOps составляет...\n\n"
        else:
            base_letter += "Мой опыт и навыки соответствуют вашим требованиям...\n\n"

        base_letter += "С уважением,\n[Ваше имя]"

        if custom_text:
            base_letter += f"\n\nP.S. {custom_text}"

        return base_letter