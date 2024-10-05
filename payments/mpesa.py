import base64
import datetime
import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth
from django.contrib import messages
from django.shortcuts import render

def generate_access_token():
    url = settings.MPESA_AUTH_URL
    response = requests.get(url, auth=HTTPBasicAuth(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
    
    if response.status_code == 200:
        json_response = response.json()
        access_token = json_response.get('access_token')
        if access_token:
            return access_token
        else:
            raise Exception("Access token not found in the response.")
    else:
        raise Exception(f"Failed to generate access token. Status code: {response.status_code}, Response: {response.text}")

def lipa_na_mpesa(request, phone_number, amount, account_reference):
    try:
        access_token = generate_access_token()  # Call the token generation function
    except Exception as e:
        messages.error(request, f"Error generating access token: {e}")
        return

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
        "CallBackURL": "https://yourdomain.com/payments/confirmation/",  # Callback URL for payment status
        "AccountReference": account_reference,
        "TransactionDesc": "Payment for order"
    }

    # Send the request
    response = requests.post(settings.MPESA_STK_PUSH_URL, json=payload, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        try:
            response_data = response.json()
            if 'errorCode' in response_data:
                messages.error(request, "Request failed: " + response_data.get('errorMessage', 'Unknown error'))
            else:
                messages.success(request, "Request was successfully sent.")
        except ValueError:
            messages.error(request, "Invalid JSON response received.")
    else:
        messages.error(request, f"Failed to initiate payment. Status code: {response.status_code}")

    # Redirect back to payment.html
    return render(request, 'payments/payment.html')
