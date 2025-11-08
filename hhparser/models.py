from django.db import models


class Vacancy(models.Model):
    """
    Модель для хранения данных о вакансиях.

    Содержит основную информацию о вакансиях, полученных с hh.ru.
    Поддерживает различные стили оформления данных для разных целей.
    Обеспечивает хранение и организацию данных для последующего анализа.
    """
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
    salary = models.CharField(max_length=150, verbose_name="Зарплата", default="Не указана")
    description = models.TextField(verbose_name="Описание", blank=True)
    experience = models.CharField(max_length=10, choices=EXPERIENCE_CHOICES, verbose_name="Опыт работы")
    employment = models.CharField(max_length=10, choices=EMPLOYMENT_CHOICES, verbose_name="Тип занятости")
    skills = models.TextField(verbose_name="Навыки", blank=True)
    link = models.URLField(verbose_name="Ссылка на вакансию", unique=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    # Стилизованные поля
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
        # Очистка ссылки перед сохранением
        if self.link:
            self.link = self.link.strip()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ['-created_at']