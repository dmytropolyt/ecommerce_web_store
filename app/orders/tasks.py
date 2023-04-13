from django.core.mail import send_mail
from celery import shared_task
from django.template.loader import render_to_string
from django.conf import settings


@shared_task()
def send_order_email(data: dict):
    """
    Send email by celery-beat to user with information about order.
    """
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_received_email.html', data)
    to_email = data['email']

    send_mail(
        mail_subject, message, from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email], fail_silently=True
    )
