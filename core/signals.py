from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import User, Organizations, Customers, Events


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if instance.role == 'client':
        if created:
            Customers.objects.create(user=instance)
        else:
            Customers.objects.save()
    else:
        if created:
            Organizations.objects.create(user=instance)
        else:
            instance.organizations.save()


@receiver(post_save, sender=Events)
def add_employees_event(sender, instance, created, **kwargs):
    if created:
        for employee in instance.employees_queryset:
            instance.employees.add(employee)

