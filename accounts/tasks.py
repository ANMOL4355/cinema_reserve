from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


@shared_task(ignore_result=True)
def send_otp_email(user_email, code, expiry_minutes):
    subject = "Your CinemaReserve verification code"

    # Plain-text fallback for email clients that don't render HTML
    text_message = (
        f"Your CinemaReserve verification code is: {code}\n\n"
        f"It expires in {expiry_minutes} minutes.\n\n"
        "If you didn't request this, you can safely ignore this email."
    )

    html_message = render_to_string(
        "accounts/emails/otp_email.html",
        {"code": code, "expiry_minutes": expiry_minutes},
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user_email],
    )
    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=False)