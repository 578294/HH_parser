from django.db import models


class Vacancy(models.Model):
    EXPERIENCE_CHOICES = [
        ('no', 'Нет опыта'),
        ('1-3', '1-3 года'),
        ('3-6', '3-6 лет'),
        ('6+', 'Более 6 лет'),
    ]

    EMPLOYMENT_CHOICES = [
        ('full', 'Полная занятость'),
        ('part', 'Частичная занятость'),
        ('remote', 'Удаленная работа'),
        ('project', 'Проектная работа'),
    ]

    title = models.CharField(max_length=255, verbose_name="Название вакансии")
    company = models.CharField(max_length=255, verbose_name="Компания")
    salary = models.CharField(max_length=100, verbose_name="Зарплата", default="Не указана")
    description = models.TextField(verbose_name="Описание", blank=True)
    experience = models.CharField(max_length=10, choices=EXPERIENCE_CHOICES, verbose_name="Опыт работы")
    employment = models.CharField(max_length=10, choices=EMPLOYMENT_CHOICES, verbose_name="Тип занятости")
    skills = models.TextField(verbose_name="Навыки", blank=True)
    link = models.URLField(verbose_name="Ссылка на вакансию", unique=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    # Стилизованные данные для разных тем
    hp_title = models.CharField(max_length=255, blank=True, verbose_name="Название (HP)")
    hp_company = models.CharField(max_length=255, blank=True, verbose_name="Компания (HP)")
    hp_salary = models.CharField(max_length=100, blank=True, verbose_name="Зарплата (HP)")

    sp_title = models.CharField(max_length=255, blank=True, verbose_name="Название (SP)")
    sp_company = models.CharField(max_length=255, blank=True, verbose_name="Компания (SP)")
    sp_salary = models.CharField(max_length=100, blank=True, verbose_name="Зарплата (SP)")

    wh_title = models.CharField(max_length=255, blank=True, verbose_name="Название (WH)")
    wh_company = models.CharField(max_length=255, blank=True, verbose_name="Компания (WH)")
    wh_salary = models.CharField(max_length=100, blank=True, verbose_name="Зарплата (WH)")

    def __str__(self):
        return f"{self.title} - {self.company}"

    def save(self, *args, **kwargs):
        # Автогенерация стилизованных данных при сохранении
        if not self.hp_title:
            self.hp_title = self.generate_hp_title()
        if not self.sp_title:
            self.sp_title = self.generate_sp_title()
        if not self.wh_title:
            self.wh_title = self.generate_wh_title()

        if not self.hp_salary:
            self.hp_salary = self.generate_hp_salary()
        if not self.sp_salary:
            self.sp_salary = self.generate_sp_salary()
        if not self.wh_salary:
            self.wh_salary = self.generate_wh_salary()

        super().save(*args, **kwargs)

    def generate_hp_title(self):
        """Генерация названия в стиле Гарри Поттера"""
        hp_prefixes = ["МАГИЧЕСКИЙ ", "ВОЛШЕБНЫЙ ", "ЗАКЛИНАТЕЛЬ "]
        hp_suffixes = [" (СТИЛЬ ХОГВАРТСА)", " В МИРЕ МАГИИ", " (ОТДЕЛ ТАЙН)"]

        base_title = self.title.upper()
        import random
        return random.choice(hp_prefixes) + base_title + random.choice(hp_suffixes)

    def generate_sp_title(self):
        """Генерация названия в стиле South Park"""
        sp_prefixes = ["КРУТОЙ ", "ОФИГЕННЫЙ ", "КАК У КАРТМАНА: "]
        sp_suffixes = [" (RESPECT MY AUTHORITAH!)", " (СЕРЬЕЗНО!)", " (ИДИ КО МНЕ!)"]

        base_title = self.title.upper()
        import random
        return random.choice(sp_prefixes) + base_title + random.choice(sp_suffixes)

    def generate_wh_title(self):
        """Генерация названия в стиле Warhammer"""
        wh_prefixes = ["ИМПЕРСКИЙ ", "СВЯЩЕННЫЙ ", "ТЕХНОЖРЕЦ "]
        wh_suffixes = [" (ЗА ИМПЕРАТОРА!)", " (ПРОТИВ ЕРЕСИ)", " (ОРДО ИНКВИЗИЦИИ)"]

        base_title = self.title.upper()
        import random
        return random.choice(wh_prefixes) + base_title + random.choice(wh_suffixes)

    def generate_hp_salary(self):
        """Генерация зарплаты в стиле HP"""
        if "Не указана" in self.salary:
            return "ОПЛАТА ВОЛШЕБНЫМИ БОБАМИ"

        salary_num = ''.join(filter(str.isdigit, self.salary))
        if salary_num:
            return f"{salary_num} ГАЛЕОНОВ (ПЛЮС FELIX FELICIS)"
        return "ЗАРПЛАТА ПО ДОГОВОРЕННОСТИ (С ДАМБЛДОРОМ)"

    def generate_sp_salary(self):
        """Генерация зарплаты в стиле SP"""
        if "Не указана" in self.salary:
            return "БУДЕТ МНОГО CHEESY POOFS!"

        salary_num = ''.join(filter(str.isdigit, self.salary))
        if salary_num:
            return f"{salary_num} $ (НЕ КАК У МИСТЕРА МЕККИ!)"
        return "ЗАРПЛАТА: МАМА СКАЗАЛА НЕ ГОВОРИТЬ"

    def generate_wh_salary(self):
        """Генерация зарплаты в стиле WH"""
        if "Не указана" in self.salary:
            return "ОПЛАТА ЧЕСТЬЮ СЛУЖЕНИЯ ИМПЕРАТОРУ"

        salary_num = ''.join(filter(str.isdigit, self.salary))
        if salary_num:
            return f"{salary_num} ИМПЕРСКИХ КРОН (И СВЯЩЕННОЕ МАСЛО)"
        return "ДЕСЯТИНА В ВИДЕ ТРОННЫХ ДУКАТОВ"

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ['-created_at']


class CoverLetter(models.Model):
    TEMPLATE_CHOICES = [
        ('standard', 'Стандартный'),
        ('support', 'Поддержка'),
        ('devops', 'DevOps'),
        ('backend', 'Backend'),
        ('frontend', 'Frontend'),
        ('manager', 'Менеджер'),
        ('custom', 'Пользовательский'),
    ]

    STYLE_CHOICES = [
        ('default', 'Обычный'),
        ('HP', 'Гарри Поттер'),
        ('SP', 'South Park'),
        ('WH', 'Warhammer 40k'),
    ]

    title = models.CharField(max_length=255, verbose_name="Название")
    content = models.TextField(verbose_name="Текст письма")
    template_type = models.CharField(max_length=20, choices=TEMPLATE_CHOICES, default='standard')
    style = models.CharField(max_length=10, choices=STYLE_CHOICES, default='default')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.style})"