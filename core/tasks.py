from celery import shared_task
from .models import Reservation
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

@shared_task
def cleanup_expired_and_cancelled_reservations():
    deleted_count, _ =  Reservation.objects.filter(
        status=Reservation.STATUS_CHOICES.cancel
    ).delete()

    now = timezone.now()
    expired_delete_count, _ = Reservation.objects.filter(
        status=Reservation.STATUS_CHOICES.pending,
        expires_at__lte=now
    ).delete()

    return deleted_count,expired_delete_count


# @shared_task
# def send_receipt_in_mail(user_email, master_id, reservation_url):
    
    # send_mail( 
    #     subject="Reservation Success",
    #     message=( "Your movie reservation has been completed successfully.\n\n"
    #              f"Reservation ID: {master_id}\n\n" 
    #              "You can view your reservation details and "
    #              "download your receipt using the link below:\n\n" 
                 
    #              f"{reservation_url}\n\n" 
    #              "Thank you for choosing CinemaReserve." ), 
    #     from_email=settings.DEFAULT_FROM_EMAIL, 
    #     recipient_list=[user_email,"lelouch5544@gmail.com","anantakarkee123@gmail.com","conesih383@94an.com"], 
    #     fail_silently=False, 
    # )
    
    
@shared_task
def send_receipt_in_mail(user_email, master_id, reservation_url):
    subject = "Your CinemaReserve Reservation is Confirmed"

    recipient_list = [
        email
        for email in [
            user_email,
            "lelouch5544@gmail.com",
            "anantakarkee123@gmail.com",
            "conesih383@94an.com",
        ]
        if email
    ]

    # Plain-text fallback
    text_message = (
        "Your movie reservation has been completed successfully.\n\n"
        f"Reservation ID: {master_id}\n\n"
        "You can view your reservation details using the link below:\n\n"
        f"{reservation_url}\n\n"
        "Thank you for choosing CinemaReserve."
    )

    # Render the separate HTML template
    html_message = render_to_string(
        "core/emails/reservation_success_email.html",
        {
            "master_id": master_id,
            "reservation_url": reservation_url,
        },
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipient_list,
    )

    email.attach_alternative(html_message, "text/html")

    email.send(fail_silently=False)
    
    
    