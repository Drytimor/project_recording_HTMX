from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from allauth_app.settings import AUTH_USER_MODEL


class User(AbstractUser):

    class UserRoleChoices(models.TextChoices):
        CLIENT = 'client', 'клиент'
        ORGANIZATION = 'organization', 'организация'

    email = models.EmailField(verbose_name='Email',
                              unique=True,
                              help_text='Введите ваш Email',
                              error_messages={
                                  "unique": "такой email адрес уже зарегистрирован"}
                              )

    role = models.CharField(max_length=20,
                            choices=UserRoleChoices.choices,
                            default=UserRoleChoices.CLIENT)


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


class Customers(models.Model):

    user = models.OneToOneField(AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='customers')

    hobby = models.CharField(verbose_name='увлечения',
                             max_length=250,
                             blank=True)

    def __str__(self):
        return f"{self.__class__.__name__}"

    class Meta:
        db_table = 'customers'


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


class EmployeesManager(models.Manager):

    def get_employees_org(self, org_id):
        return self.model.objects.filter(organization_id=org_id)
        # return ' '.join([q.name for q in self.model.objects.filter(organization_id=self.instance.organization_id)])


class Employees(models.Model):

    user = models.ForeignKey(AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='employees')

    name = models.CharField(verbose_name='Имя',
                            max_length=255,
                            unique=True)

    objects = EmployeesManager()

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = 'employees'


class EventsManager(models.Manager):
    pass


class Events(models.Model):

    user = models.ForeignKey(AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='events')

    name = models.CharField(verbose_name='Название',
                            max_length=250,
                            unique=True)

    employees = models.ManyToManyField('employees',
                                       verbose_name='Сотрудник',
                                       related_name='events')

    objects = EventsManager()

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = 'events'


class StatusRecordingChoices(models.TextChoices):
    PAID = "paid", "оплачено"
    CANCELED = "canc", "отменено"


class Recordings(models.Model):

    event = models.ForeignKey('events',
                              verbose_name='Мероприятие',
                              on_delete=models.CASCADE,
                              related_name='recordings')

    user = models.ForeignKey(AUTH_USER_MODEL,
                             verbose_name='Клиент',
                             on_delete=models.CASCADE,
                             related_name='recordings')

    status_recording = models.CharField(max_length=4,
                                        verbose_name='Статус записи',
                                        choices=StatusRecordingChoices.choices)

    date_recording = models.DateTimeField(verbose_name='Дата записи',
                                          auto_now=True)

    class Meta:
        db_table = 'recordings'
        constraints = [
            models.UniqueConstraint(fields=['event', 'user'],
                                    name=f"unique_{db_table}_user")
        ]



