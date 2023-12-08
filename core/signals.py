from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import User, Organizations, Customers


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if instance.role == 'client':
        if created:
            Customers.objects.create(user=instance)
    else:
        if created:
            Organizations.objects.create(user=instance)
        # else:
        #     instance.organizations.save()

