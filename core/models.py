from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(verbose_name='Email',
                              unique=True,
                              help_text='Введите ваш Email',
                              error_messages={
                                  "unique": "такой email адрес уже зарегистрирован"}
                              )
