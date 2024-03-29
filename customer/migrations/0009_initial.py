# Generated by Django 4.2.7 on 2024-01-03 09:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organization', '0011_remove_records_recordings'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('customer', '0008_delete_recordings'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recordings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_recording', models.CharField(choices=[('paid', 'оплачено'), ('canc', 'отменено')], max_length=4, verbose_name='Статус записи')),
                ('date_recording', models.DateTimeField(auto_now=True, verbose_name='Дата записи')),
                ('record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recordings', to='organization.records', verbose_name='Мероприятие')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recordings', to=settings.AUTH_USER_MODEL, verbose_name='Клиент')),
            ],
            options={
                'db_table': 'recordings',
            },
        ),
    ]
