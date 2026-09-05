from celery import shared_task
from .models import Reservation
from django.utils import timezone

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