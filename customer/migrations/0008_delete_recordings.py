# Generated by Django 4.2.7 on 2024-01-03 09:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0007_remove_recordings_unique_recordings_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Recordings',
        ),
    ]
