from django.db import models
from allauth_app.settings import AUTH_USER_MODEL
from organization.models import Events, EventRecords


class StatusRecordingChoices(models.TextChoices):
    PAID = "paid", "оплачено"
    CANCELED = "canc", "отменено"


class Recordings(models.Model):

    event_record = models.ForeignKey(EventRecords,
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
            models.UniqueConstraint(fields=['event_record', 'user'],
                                    name=f"unique_{db_table}_user")
        ]
