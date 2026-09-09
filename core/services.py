
import requests
import json
from django.conf import settings
from django.db import transaction
from .models import Reservation, MasterReservation

def verify_khalti_payment(pidx):
   url = settings.KHALTI_LOOKUP_URL
   payload = json.dumps({
        "pidx": pidx
         })
   headers = {
         'Authorization': f'key {settings.KHALTI_API_SECRET_KEY}',
         'Content-Type': 'application/json',
      }

   response = requests.request("POST", url, headers=headers, data=payload)
   return response.json()




def initiate_khalti_payment(master, show, seats_ids, user):
    url = settings.KHALTI_INITIATE_URL

    amount = show.price * len(seats_ids) * 100  # paisa

    payload = json.dumps({
        "return_url": settings.KHALTI_RETURN_URL ,
        "website_url": settings.KHALTI_WEBSITE_URL,
        "amount": str(amount),
        "purchase_order_id": master.id,
        "purchase_order_name": "Movie Ticket",
        "customer_info": {
            "name": user.get_full_name() or user.username,
            "email": user.email,
            "phone": "9800000001"
        }
    })

    headers = {
        'Authorization': f'key {settings.KHALTI_API_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    response = requests.request( "POST", url, headers=headers, data=payload)
    data = response.json()

    return data, amount

