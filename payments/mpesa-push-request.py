# payments/mpesa.py
import base64
import datetime
import requests
from django.conf import settings

def lipa_na_mpesa(phone_number, amount, account_reference):
    access_token = generate_access_token()
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(
        f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()
    ).decode('utf-8')

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,  # User's phone number (format 2547xxxxxxxx)
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://yourdomain.com/payments/confirmation/",  # This is the callback URL for payment status
        "AccountReference": account_reference,
        "TransactionDesc": "Payment for order"
    }

    response = requests.post(settings.MPESA_STK_PUSH_URL, json=payload, headers=headers)
    return response.json()
