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
        ordering = ['name']


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


class Records(models.Model):

    events = models.ForeignKey('events',
                               on_delete=models.CASCADE,
                               related_name='records')

    limit_clients = models.SmallIntegerField()

    quantity_clients = models.SmallIntegerField(default=0)

    datetime = models.DateTimeField()

    class Meta:
        db_table = 'records'


class PaymentTariffChoices(models.TextChoices):
    PAID = "paid", "платный"
    FREE = "free", "бесплатный"


class Events(models.Model):

    organization = models.ForeignKey('organizations',
                                     on_delete=models.CASCADE,
                                     related_name='events')

    name = models.CharField(verbose_name='Название',
                            max_length=250)

    employees = models.ManyToManyField('employees',
                                       verbose_name='Сотрудник',
                                       related_name='events')

    status_tariff = models.CharField(max_length=4,
                                     choices=PaymentTariffChoices.choices)

    price = models.DecimalField(verbose_name='Цена',
                                max_digits=10,
                                decimal_places=2,
                                null=True)

    is_active = models.BooleanField(default=False)

    objects = EventsManager()

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = 'events'
        ordering = ['name']

