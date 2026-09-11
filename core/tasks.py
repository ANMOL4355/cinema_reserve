from celery import shared_task
from .models import Reservation
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import qrcode
from io import BytesIO
from email.mime.image import MIMEImage

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
    
    # Generate QR code containing only master_id
    qr_data = str(master_id)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )

    qr.add_data(qr_data)
    qr.make(fit=True)

    qr_image = qr.make_image(
        fill_color="black",
        back_color="white",
    )
    
    # Keep the QR code in memory
    qr_buffer = BytesIO()
    qr_image.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)


    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipient_list,
    )
    email.attach_alternative(html_message, "text/html")
    
     # Attach QR code for displaying inside the email
    inline_qr_attachment = MIMEImage( qr_buffer.getvalue(), _subtype="png",)
    inline_qr_attachment.add_header("Content-ID","<reservation_qr>",)
    inline_qr_attachment.add_header("Content-Disposition","inline",filename=f"reservation_{master_id}_qr.png",)
    email.attach(inline_qr_attachment)

     # Attach QR code as a downloadable file
    downloadable_qr_attachment = MIMEImage(qr_buffer.getvalue(), _subtype="png",)
    downloadable_qr_attachment.add_header("Content-Disposition","attachment",filename=f"reservation_{master_id}_qr.png",)
    email.attach(downloadable_qr_attachment)

    # Send email
    email.send(fail_silently=False)
    
    
    