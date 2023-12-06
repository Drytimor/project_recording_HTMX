from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.shortcuts import reverse
from allauth_app.settings import AUTH_USER_MODEL


class User(AbstractUser):
    email = models.EmailField(verbose_name='Email',
                              unique=True,
                              help_text='Введите ваш Email',
                              error_messages={
                                  "unique": "такой email адрес уже зарегистрирован"}
                              )


class Organizations(models.Model):

    user = models.OneToOneField(AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='organizations')

    name = models.CharField(verbose_name='Название',
                            max_length=255,
                            unique=True,
                            error_messages={
                                'unique': 'такая организация уже зарегистрирована'}
                            )

    category = models.ForeignKey('categories',
                                 verbose_name='Категория',
                                 on_delete=models.SET_NULL,
                                 related_name='organizations',
                                 null=True)

    def save(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = 'organizations'


class CategoriesChoices(models.TextChoices):
    SPORT = "sport", "спорт"
    TOURISM = "tourism", "туризм"
    EDUCATION = "education", "образование"
    SCIENCE = "science", "наука"
    ENTERTAINMENT = "entertainment", "развлечение"
    SUNDRY = "sundry", "разное"


class Categories(models.Model):
    name = models.CharField(max_length=50,
                            choices=CategoriesChoices.choices)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = 'categories'
        constraints = [
            models.CheckConstraint(check=Q(name__in=CategoriesChoices.values),
                                   name=f"check_{db_table}")
        ]
