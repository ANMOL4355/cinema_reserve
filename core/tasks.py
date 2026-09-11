from celery import shared_task
from .models import Reservation
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

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


@shared_task
def send_receipt_in_mail(user_email, master_id, reservation_url):
    
    send_mail( 
        subject="Reservation Success",
        message=( "Your movie reservation has been completed successfully.\n\n"
                 f"Reservation ID: {master_id}\n\n" 
                 "You can view your reservation details and "
                 "download your receipt using the link below:\n\n" 
                 
                 f"{reservation_url}\n\n" 
                 "Thank you for choosing CinemaReserve." ), 
        from_email=settings.DEFAULT_FROM_EMAIL, 
        recipient_list=[user_email,"lelouch5544@gmail.com","vefegib744@daugr.com"], 
        fail_silently=False, 
    )
    
    