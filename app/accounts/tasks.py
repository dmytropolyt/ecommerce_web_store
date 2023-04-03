from django.core.mail import send_mail
from celery import shared_task
from django.conf import settings


@shared_task()
def send_activation_email(mail_subject: str, message: str, to_email: str):
    """
    Send activation email with celery.
    """
    send_mail(
        mail_subject, message, from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email], fail_silently=True
    )
