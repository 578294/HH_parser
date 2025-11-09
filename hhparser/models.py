"""
Модуль models.py содержит модели данных для приложения hhparser.

Основная модель:
- Vacancy: модель для хранения данных о вакансиях с HeadHunter
  с полями для основной информации, опыта работы, типа занятости и навыков.
"""
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

    def __str__(self) -> str:
        """
        Строковое представление вакансии.

        Returns:
            str: строка в формате "Название - Компания"
        """
        return f"{self.title} - {self.company}"

    def save(self, *args, **kwargs) -> None:
        """
        Переопределенный метод сохранения с очисткой ссылки.

        Args:
            *args: позиционные аргументы
            **kwargs: именованные аргументы
        """
        if self.link:
            self.link = self.link.strip()
        super().save(*args, **kwargs)

    class Meta:
        """Мета-класс для настроек модели Vacancy."""

        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ['-created_at']