# a_stripe/views.py
import stripe
import os # <--- AJOUT IMPORTANT
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from transport.models import Commande


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
                        'unit_amount': int(commande.prix_total * 100),
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