# Generated by Django 4.2.7 on 2024-01-08 08:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0013_records_events'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('customer', '0010_recordings_unique_recordings_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignedEvents',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_events', to='organization.events')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_events', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'assigned_events',
            },
        ),
        migrations.AddConstraint(
            model_name='assignedevents',
            constraint=models.UniqueConstraint(fields=('user', 'event'), name='unique_assigned_events_user'),
        ),
    ]