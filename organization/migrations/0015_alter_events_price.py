# Generated by Django 4.2.7 on 2024-01-14 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0014_events_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='events',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True, verbose_name='Цена'),
        ),
    ]
