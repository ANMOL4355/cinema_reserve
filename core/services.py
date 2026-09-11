
import requests
import json
from django.conf import settings
from django.db import transaction
from .models import Reservation, MasterReservation

def verify_khalti_payment(pidx):
    url = settings.KHALTI_LOOKUP_URL
    payload = {
        "pidx": pidx
         }
    headers = {
         'Authorization': f'key {settings.KHALTI_API_SECRET_KEY}',
         'Content-Type': 'application/json',
      }

    response = requests.post( url, headers=headers, json=payload,timeout=15)
    
    print("KHALTI LOOKUP STATUS:", response.status_code)
    print("KHALTI LOOKUP RESPONSE:", response.text)

    
    try:
       data=response.json()
    except ValueError:
        raise Exception(
            f"Khalti lookup returned invalid JSON:{response.text}"
        )
    if response.status_code != 200:
        raise Exception(
            f"khalti lookup failed:{data}"
        )
    
       
    return data




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

    response = requests.post(
    url,
    headers=headers,
    data=payload,
    timeout=15
)

    print("KHALTI INITIATE STATUS:", response.status_code)
    print("KHALTI INITIATE RESPONSE:", response.text)

    try:
        data = response.json()
    except ValueError:
        raise Exception(
            f"Khalti returned invalid JSON: {response.text}"
        )

    if response.status_code != 200:
        raise Exception(
            f"Khalti initiation failed: {data}"
        )

    if not data.get("pidx"):
        raise Exception(
            f"Khalti did not return pidx: {data}"
        )

    if not data.get("payment_url"):
        raise Exception(
            f"Khalti did not return payment_url: {data}"
        )

    return data, amount

