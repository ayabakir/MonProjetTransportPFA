# transport/utils.py
from django.db.models import Q
from .models import Livraison
from datetime import timedelta

def verifier_disponibilite(vehicule, chauffeur, date_debut, duree_heures):
    """
    Vérifie si un véhicule et un chauffeur sont disponibles
    pendant la période spécifiée
    """
    date_fin = date_debut + timedelta(hours=float(duree_heures))
    
    # Vérifier les conflits pour le véhicule
    conflits_vehicule = Livraison.objects.filter(
        vehicule=vehicule,
        date_planification_debut__lt=date_fin,
        date_planification_fin_estimee__gt=date_debut
    ).exists()
    
    # Vérifier les conflits pour le chauffeur
    conflits_chauffeur = Livraison.objects.filter(
        chauffeur=chauffeur,
        date_planification_debut__lt=date_fin,
        date_planification_fin_estimee__gt=date_debut
    ).exists()
    
    return not (conflits_vehicule or conflits_chauffeur)