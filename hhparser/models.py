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

    def __str__(self):
        return f"{self.title} - {self.company}"

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ['-created_at']


# class CoverLetter(models.Model):
#     title = models.CharField(max_length=255, verbose_name="Название")
#     content = models.TextField(verbose_name="Текст сопроводительного письма")
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.title
