# a_stripe/urls.py

from django.urls import path
from . import views

# Le nom de l'espace de noms pour cette application, très important !
app_name = 'a_stripe'

urlpatterns = [
    # IMPORTANT : Ces URLs sont relatives à l'application 'a_stripe'.
    # Le chemin sera donc /paiement/create-checkout-session/...
    path('create-checkout-session/<int:commande_id>/', views.create_checkout_session, name='create-checkout-session'),
    path('success/', views.payment_success, name='payment-success'),
    path('cancel/', views.payment_cancel, name='payment-cancel'),
    
    # Ajoutez ici plus tard l'URL pour le webhook
    # path('webhook/', views.stripe_webhook, name='stripe-webhook'),
]