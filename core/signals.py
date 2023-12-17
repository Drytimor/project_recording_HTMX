
# @receiver(post_save, sender=Events)
# def add_employees_event(sender, instance, created, **kwargs):
#     if created:
#         for employee in instance.employees_queryset:
#             instance.employees.add(employee)


# @receiver(post_save, sender=Organizations)
# def created_organization_user(sender, instance, **kwargs):
#     instance.user.organization_created = True
#     instance.user.save(update_fields=['organization_created'])


# @receiver(post_delete, sender=Organizations)
# def custom_cascade_delete_organization(sender, instance, **kwargs):
#     instance.user.employees.all().delete()
#     instance.user.events.all().delete()
#     instance.user.organization_created = False
#     instance.user.save(update_fields=['organization_created'])



