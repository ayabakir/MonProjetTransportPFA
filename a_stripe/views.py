# a_stripe/views.py
import stripe
import os # <--- AJOUT IMPORTANT
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from transport.models import Commande


def create_checkout_session(request, commande_id):
    """
    Cette vue crée la session de paiement Stripe et redirige l'utilisateur.
    """
    # === LA SOLUTION ULTIME ===
    # On ignore settings et on lit la clé DIRECTEMENT depuis les variables d'environnement.
    # C'est la méthode la plus directe et la plus sûre.
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

    # --- DEBUG POUR VÉRIFIER ---
    # Cette ligne est notre test final.
    print(f"--- DEBUG FINAL: Clé lue directement depuis l'environnement : '{stripe.api_key}' ---")
    if not stripe.api_key:
        return HttpResponse("ERREUR CRITIQUE : La variable STRIPE_SECRET_KEY est vide ou n'est pas trouvée dans l'environnement. Vérifiez votre fichier .env et redémarrez le serveur.", status=500)


    # 1. Récupérer la commande
    commande = get_object_or_404(Commande, pk=commande_id)

    # 2. Vérifier le montant
    if not commande.montant_total or commande.montant_total <= 0:
        return HttpResponse("Erreur : Le montant de la commande n'est pas valide.", status=400)

    # 3. Convertir en centimes
    montant_en_centimes = int(commande.montant_total * 100)

    # 4. URLs
    YOUR_DOMAIN = "https://ayaba.pythonanywhere.com"
    success_url = YOUR_DOMAIN + '/paiement/success/'
    cancel_url = YOUR_DOMAIN + '/paiement/cancel/'

    try:
        # 5. Créer la session Stripe
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'mad',
                    'unit_amount': montant_en_centimes,
                    'product_data': {
                        'name': f'Paiement pour Commande #{commande.reference_commande_or_id()}',
                        'description': commande.description_marchandise,
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=cancel_url,
            metadata={'commande_id': commande.id}
        )
        return HttpResponseRedirect(checkout_session.url)
    except Exception as e:
        return HttpResponse(f"Erreur lors de la création de la session de paiement : {e}", status=500)


def payment_success(request):
    return render(request, 'a_stripe/payment_success.html')


def payment_cancel(request):
    return render(request, 'a_stripe/payment_cancel.html')