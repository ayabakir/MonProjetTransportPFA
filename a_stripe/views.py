# a_stripe/views.py
import stripe
import os # <--- AJOUT IMPORTANT
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from transport.models import Commande
from django.urls import path, reverse


def create_checkout_session(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)

    # On définit le domaine de notre site en production
    YOUR_DOMAIN = 'https://ayaba.pythonanywhere.com'

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'mad', # ou 'eur', etc.
                        'product_data': {
                            'name': f'Paiement pour commande #{commande.id}',
                        },
                        'unit_amount': int(commande.montant_total * 100),
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            
            # On construit les URLs complètes pour la redirection
            success_url=YOUR_DOMAIN + reverse('a_stripe:payment-success'),
            cancel_url=YOUR_DOMAIN + reverse('a_stripe:payment-cancel'),
        )
        # On renvoie l'ID de la session au JavaScript côté client
        return JsonResponse({'id': checkout_session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def payment_success(request):
    return render(request, 'a_stripe/payment_success.html')


def payment_cancel(request):
    return render(request, 'a_stripe/payment_cancel.html')
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event (e.g., payment succeeded)
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']