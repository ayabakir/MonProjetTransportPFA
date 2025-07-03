from django.db import models

# Create your models here.
# MONPROJETTRANSPORTPFA/a_stripe/models.py

from django.db import models
from django.conf import settings # Bonne pratique pour lier à votre modèle User
# Important : Utiliser une chaîne de caractères pour la liaison afin d'éviter les importations circulaires
# 'transport.Commande' est la bonne façon de faire référence à un modèle dans une autre app.

class StripeCustomer(models.Model):
    """
    Lie un utilisateur Django à un objet Customer de Stripe.
    Cela permet de réutiliser les informations du client pour de futurs paiements.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='stripe_customer',
        verbose_name="Utilisateur"
    )
    stripe_customer_id = models.CharField(
        max_length=255, 
        unique=True, 
        blank=True, 
        null=True,
        verbose_name="ID Client Stripe"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Client Stripe pour {self.user.username}"

    class Meta:
        verbose_name = "Client Stripe"
        verbose_name_plural = "Clients Stripe"


class StripePayment(models.Model):
    """
    Représente une transaction de paiement spécifique via Stripe pour une Commande.
    """
    # Relation clé : un paiement est pour une commande spécifique.
    commande = models.OneToOneField(
        'transport.Commande',  # Référence au modèle Commande dans l'app 'transport'
        on_delete=models.SET_NULL, # Si la commande est supprimée, on garde une trace du paiement
        null=True,
        blank=True, # Peut être créé avant d'être lié à une commande si besoin
        related_name='stripe_payment',
        verbose_name="Commande Associée"
    )
    # On peut aussi garder un lien vers le client Stripe pour un accès rapide
    stripe_customer = models.ForeignKey(
        StripeCustomer, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name="Client Stripe"
    )

    # Identifiants Stripe
    # Le Payment Intent est l'objet central dans les flux de paiement modernes de Stripe
    stripe_payment_intent_id = models.CharField(
        max_length=255, 
        unique=True,
        verbose_name="ID Payment Intent Stripe"
    )
    
    # Informations sur le paiement au moment de la transaction
    montant = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Montant"
    )
    currency = models.CharField(
        max_length=3, 
        default='eur', # Mettez votre devise par défaut
        verbose_name="Devise"
    )

    # Statut du paiement (plus détaillé qu'un simple booléen 'has_paid')
    STATUT_PAIEMENT_CHOICES = [
        ('requires_payment_method', 'En attente de méthode de paiement'),
        ('requires_confirmation', 'En attente de confirmation'),
        ('requires_action', 'Action requise par le client'),
        ('processing', 'En cours de traitement'),
        ('succeeded', 'Réussi'),
        ('canceled', 'Annulé'),
        ('failed', 'Échoué'),
    ]
    statut = models.CharField(
        max_length=30,
        choices=STATUT_PAIEMENT_CHOICES,
        default='requires_payment_method',
        verbose_name="Statut du Paiement"
    )
    
    # Horodatages
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_paiement_reussi = models.DateTimeField(null=True, blank=True, verbose_name="Date du paiement réussi")

    def __str__(self):
        ref_commande = self.commande.reference_commande if self.commande else "N/A"
        return f"Paiement {self.statut} de {self.montant} {self.currency.upper()} pour Commande {ref_commande}"

    class Meta:
        verbose_name = "Paiement Stripe"
        verbose_name_plural = "Paiements Stripe"
        ordering = ['-date_creation']