from django.db import models
from django.utils import timezone


class Vacancy(models.Model):
    EXPERIENCE_CHOICES = [
        ('no', 'Без опыта'),
        ('1-3', '1-3 года'),
        ('3-6', '3-6 лет'),
        ('6+', 'Более 6 лет'),
    ]

    EMPLOYMENT_CHOICES = [
        ('full', 'Полная'),
        ('part', 'Частичная'),
        ('remote', 'Удаленная'),
        ('project', 'Проектная'),
    ]

    title = models.CharField(max_length=255, verbose_name="Название вакансии")
    company = models.CharField(max_length=255, verbose_name="Компания")
    salary = models.CharField(max_length=100, verbose_name="Зарплата", blank=True)
    description = models.TextField(verbose_name="Описание")
    experience = models.CharField(max_length=10, choices=EXPERIENCE_CHOICES, verbose_name="Опыт")
    employment = models.CharField(max_length=10, choices=EMPLOYMENT_CHOICES, verbose_name="Тип занятости")
    skills = models.TextField(verbose_name="Ключевые навыки", blank=True)
    link = models.URLField(verbose_name="Ссылка", unique=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.company}"


class CoverLetter(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, verbose_name="Вакансия")
    template_type = models.CharField(max_length=50, verbose_name="Тип шаблона")
    content = models.TextField(verbose_name="Текст письма")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Сопроводительное письмо"
        verbose_name_plural = "Сопроводительные письма"

    def __str__(self):
        return f"Письмо для {self.vacancy.title}"