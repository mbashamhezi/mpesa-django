# payments/views.py
from django.shortcuts import render
from .mpesa import lipa_na_mpesa
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



def home(request):
    return render(request, 'payments/payment.html')


def initiate_payment(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone')
        amount = request.POST.get('amount')
        account_reference = request.POST.get('account_reference')

        # Call the M-Pesa integration function
        lipa_na_mpesa(request, phone_number, amount, account_reference)

    return render(request, 'payments/payment.html')



@csrf_exempt
def payment_confirmation(request):
    if request.method == 'POST':
        payment_data = request.body.decode('utf-8')
        # Process the payment result
        return JsonResponse({"Result": "Success"})
