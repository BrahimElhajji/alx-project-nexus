from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from .models import Application, Notification

@receiver(pre_save, sender=Application)
def _capture_old_application_status(sender, instance, **kwargs):
    """
    Before saving an Application, capture old status (if it exists) so we can
    compare after save in post_save.
    """
    if instance.pk:
        try:
            old = Application.objects.get(pk=instance.pk)
            instance._old_status = old.status
        except Application.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

@receiver(post_save, sender=Application)
def create_notifications_on_application_events(sender, instance, created, **kwargs):
    """
    - When an application is created: notify the employer.
    - When an existing application's status changes: notify the applicant.
    """
    # 1) New application created -> notify employer
    if created:
        employer = instance.job.employer
        applicant = instance.applicant
        message = f"New application from {applicant.username} for '{instance.job.title}'."
        # Use relative URL instead of hardcoded localhost
        url = f"/api/applications/{instance.pk}/"
        Notification.objects.create(user=employer, message=message, url=url)
        return

    # 2) Status changed -> notify applicant
    old_status = getattr(instance, "_old_status", None)
    if old_status is not None and old_status != instance.status:
        applicant = instance.applicant
        message = f"Your application for '{instance.job.title}' is now '{instance.status}'."
        url = f"/api/applications/{instance.pk}/"
        Notification.objects.create(user=applicant, message=message, url=url)
