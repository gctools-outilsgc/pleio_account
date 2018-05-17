from django.core.mail import send_mail as django_send_mail
from django.conf import settings
from celery import shared_task

@shared_task
def send_mail(subject, message, from_email, recipient_list, **kwargs):
    return django_send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        **kwargs
    )