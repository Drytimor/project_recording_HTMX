# Generated by Django 4.2.7 on 2024-01-05 13:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0011_remove_records_recordings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='events',
            name='record',
        ),
    ]
