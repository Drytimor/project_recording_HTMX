from django.db import models
from django.db.models import Q

from allauth_app.settings import AUTH_USER_MODEL


class Organizations(models.Model):

    user = models.OneToOneField(AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='organizations')

    name = models.CharField(verbose_name='Название',
                            max_length=255,
                            error_messages={
                                'unique': 'такая организация уже зарегистрирована'},
                            blank=True)

    category = models.ForeignKey('categories',
                                 verbose_name='Категория',
                                 on_delete=models.SET_NULL,
                                 related_name='organizations',
                                 null=True)

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
                            choices=CategoriesChoices.choices,
                            default=CategoriesChoices.SUNDRY)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = 'categories'
        constraints = [
            models.CheckConstraint(check=Q(name__in=CategoriesChoices.values),
                                   name=f"check_{db_table}")
        ]


class Employees(models.Model):

    organization = models.ForeignKey('organizations',
                                     on_delete=models.CASCADE,
                                     related_name='employees')

    name = models.CharField(verbose_name='Имя',
                            max_length=255,
                            unique=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = 'employees'


class EventsManager(models.Manager):
    pass


class EventRecords(models.Model):

    event = models.ManyToManyField('events',
                                   related_name='event_records')

    limit_clients = models.SmallIntegerField()

    quantity_clients = models.SmallIntegerField(default=0)

    datetime = models.DateTimeField()

    class Meta:
        db_table = 'event_records'


class Events(models.Model):

    organization = models.ForeignKey('organizations',
                                     on_delete=models.CASCADE,
                                     related_name='events')

    name = models.CharField(verbose_name='Название',
                            max_length=250)

    employees = models.ManyToManyField('employees',
                                       verbose_name='Сотрудник',
                                       related_name='events')

    is_active = models.BooleanField(default=False)

    objects = EventsManager()

    def __str__(self):
        return f"{self.name}"

    def delete(self, *args, **kwargs):
        a = 'a'
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'events'
