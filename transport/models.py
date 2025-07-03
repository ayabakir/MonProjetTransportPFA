# MONPROJETTRANSPORTPFA/transport/models.py
from django.db import models
from django.contrib.auth.models import User # Utilisé pour lier les profils
from django.utils import timezone # Utile pour les dates par défaut ou les comparaisons
from datetime import timedelta
# --- Utilisateurs et Profils ---

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="Utilisateur Associé")
    adresse_facturation = models.TextField(blank=True, null=True, verbose_name="Adresse de Facturation")
    preferences_contact = models.CharField(max_length=50, blank=True, null=True, verbose_name="Préférences de Contact")
    notes_client = models.TextField(blank=True, null=True, verbose_name="Notes sur le Client")
    photo_profil = models.ImageField(upload_to='profils_clients/', blank=True, null=True)

    def __str__(self):
        return f"Client: {self.user.username}"

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

class Chauffeur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="Utilisateur Associé")
    numero_permis = models.CharField(max_length=50, unique=True, verbose_name="Numéro de Permis")
    date_expiration_permis = models.DateField(null=True, blank=True, verbose_name="Date d'Expiration du Permis")
    DISPONIBILITE_CHOICES = [
        ('disponible', 'Disponible'),
        ('en_mission', 'En Mission'),
        ('en_repos', 'En Repos'),
    ]
    disponibilite_statut = models.CharField(
        max_length=20,
        choices=DISPONIBILITE_CHOICES,
        default='disponible',
        verbose_name="Statut de Disponibilité"
    )
    notes_chauffeur_profil = models.TextField(blank=True, null=True, verbose_name="Notes sur le Chauffeur")

    def __str__(self):
        return f"Chauffeur: {self.user.username}"

    class Meta:
        verbose_name = "Chauffeur"
        verbose_name_plural = "Chauffeurs"

class GestionnaireLogistique(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="Utilisateur Associé")
    matricule_employe = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name="Matricule Employé")
    telephone_professionnel = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone Professionnel")

    def __str__(self):
        return f"Gestionnaire: {self.user.username}"

    class Meta:
        verbose_name = "Gestionnaire Logistique"
        verbose_name_plural = "Gestionnaires Logistiques"

# --- Partenaires et Ressources ---

class Transporteur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Compte Utilisateur Associé") # Modifié pour la cohérence
    nom = models.CharField(max_length=100, verbose_name="Nom du Responsable/Contact") # Modifié verbose_name
    nom_entreprise = models.CharField(max_length=200, unique=True, verbose_name="Nom de l'Entreprise")
    adresse = models.TextField(blank=True, null=True, verbose_name="Adresse")
    contact_email = models.EmailField(blank=True, null=True, verbose_name="Email de Contact (Affichage)") # Modifié verbose_name
    contact_telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone de Contact")
    details_contrat = models.TextField(blank=True, null=True, verbose_name="Détails du Contrat")
    date_inscription = models.DateTimeField(auto_now_add=True, verbose_name="Date d'Enregistrement") # Modifié verbose_name
    photo_profil = models.ImageField(upload_to='profils_transporteurs/', blank=True, null=True, verbose_name="Photo de profil")

    def __str__(self):
        return self.nom_entreprise # Simplifié, le nom du responsable peut être dans user.get_full_name()

    class Meta:
        verbose_name = "Transporteur (Partenaire)"
        verbose_name_plural = "Transporteurs (Partenaires)"


class Vehicule(models.Model):
    transporteur = models.ForeignKey(
        Transporteur,
        on_delete=models.SET_NULL, 
        null=True,
        blank=True, # Permet de créer un véhicule non assigné, ou pour votre propre flotte
        related_name='vehicules',
        verbose_name="Transporteur Propriétaire"
    )
    immatriculation = models.CharField(max_length=20, unique=True, verbose_name="Immatriculation")
    type_vehicule = models.CharField(max_length=100, verbose_name="Type de Véhicule")
    capacite_poids_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Capacité Poids (kg)")
    capacite_volume_m3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Capacité Volume (m³)")
    STATUT_VEHICULE_CHOICES = [
        ('disponible', 'Disponible'),
        ('en_mission', 'En Mission'),
        ('en_maintenance', 'En Maintenance'),
    ]
    statut_vehicule = models.CharField(
        max_length=20,
        choices=STATUT_VEHICULE_CHOICES,
        default='disponible',
        verbose_name="Statut du Véhicule"
    )
    localisation_actuelle = models.CharField(max_length=255, blank=True, null=True, verbose_name="Localisation Actuelle")
    consommation_moyenne_l_100km = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Consommation (L/100km)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    def __str__(self):
        return self.immatriculation

    class Meta:
        verbose_name = "Véhicule"
        verbose_name_plural = "Véhicules"
        ordering = ['immatriculation']

# Fichier : transport/models.py
# ... (gardez tous les autres modèles comme Client, Chauffeur, etc.)

class Commande(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='commandes', verbose_name="Client")
    reference_commande = models.CharField(max_length=50, unique=True, blank=True, verbose_name="Référence Commande")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    description_marchandise = models.TextField(verbose_name="Description Marchandise")
    poids_kg = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Poids (kg)")
    volume_m3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Volume (m³)")
    adresse_chargement = models.TextField(verbose_name="Adresse de Chargement")
    adresse_livraison = models.TextField(verbose_name="Adresse de Livraison")
    date_souhaitee_livraison = models.DateField(verbose_name="Date Souhaitée de Livraison")
    
    STATUT_COMMANDE_CHOICES = [
        ('en_attente_validation', 'En attente de validation'),
        ('paiement_en_attente', 'En attente de paiement'), # Statut après calcul du prix
        ('validee', 'Payée (Validée)'), # Nouveau nom pour plus de clarté
        ('planifiee', 'Planifiée'),
        ('en_cours_livraison', 'En cours de livraison'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]
    statut_commande = models.CharField(
        max_length=30,
        choices=STATUT_COMMANDE_CHOICES,
        default='en_attente_validation',
        verbose_name="Statut de la Commande"
    )
    
    montant_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Montant Total (MAD)"
    )
    instructions_speciales = models.TextField(blank=True, null=True, verbose_name="Instructions Spéciales")
    motif_annulation = models.TextField(blank=True, null=True, verbose_name="Motif d'Annulation/Refus")

    def __str__(self):
        return self.reference_commande or f"Commande ID {self.id}"

    def reference_commande_or_id(self):
        return self.reference_commande or f"ID-{self.id}"

    @property
    def is_modifiable_ou_supprimable(self):
        """Détermine si une commande peut être modifiée ou supprimée par le client."""
        # Un client peut modifier/supprimer tant que la commande n'a pas été payée et planifiée
        return self.statut_commande in ['en_attente_validation', 'paiement_en_attente']

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-date_creation']


class Itineraire(models.Model):
    geometry_geojson = models.JSONField(blank=True, null=True, verbose_name="Géométrie Tracé (GeoJSON)")
    points_etapes_str = models.TextField(blank=True, null=True, verbose_name="Points Étapes (Texte/Original)")
    distance_totale_km_estimee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Distance Estimée (km)")
    duree_totale_sec_estimee = models.IntegerField(null=True, blank=True, verbose_name="Durée Estimée (secondes)")
    instructions_textuelles = models.TextField(blank=True, null=True, verbose_name="Instructions Textuelles")
    raw_ors_response = models.JSONField(blank=True, null=True, verbose_name="Réponse Brute ORS")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création") # Modifié verbose_name

    def __str__(self):
        return f"Itinéraire ID {self.id} ({self.distance_totale_km_estimee or 'N/A'} km)"

    @property
    def duree_totale_heures_estimee(self):
        if self.duree_totale_sec_estimee is not None:
            return round(self.duree_totale_sec_estimee / 3600.0, 2) # Ajout de round
        return None

    class Meta:
        verbose_name = "Itinéraire"
        verbose_name_plural = "Itinéraires"
        ordering = ['-date_creation']

class Livraison(models.Model):
    commandes = models.ManyToManyField(Commande, related_name='livraisons', verbose_name="Commandes Associées") # related_name ajusté
    vehicule = models.ForeignKey(Vehicule, on_delete=models.PROTECT, related_name='livraisons', verbose_name="Véhicule")
    chauffeur = models.ForeignKey(Chauffeur, on_delete=models.PROTECT, related_name='livraisons', verbose_name="Chauffeur")
    itineraire = models.OneToOneField(Itineraire, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Itinéraire")
    date_planification_debut = models.DateTimeField(verbose_name="Date Planification Début")
    date_planification_fin_estimee = models.DateTimeField(null=True, blank=True, verbose_name="Date Planification Fin Estimée")
    date_effective_debut = models.DateTimeField(null=True, blank=True, verbose_name="Date Effective Début") # Ajout
    date_effective_fin = models.DateTimeField(null=True, blank=True, verbose_name="Date Effective Fin")   # Ajout
    duree_estimee_heures = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        default=4.0,
        verbose_name="Durée estimée (heures)"
    )
    STATUT_LIVRAISON_CHOICES = [
        ('planifiee', 'Planifiée'),
        ('en_attente_chargement', 'En attente de chargement'), # Ajout possible
        ('en_cours_chargement', 'En cours de chargement'),
        ('en_transit', 'En transit'),
        # ('livree_partiellement', 'Livrée partiellement'), # Peut-être pas nécessaire si une livraison = une tournée
        ('arrivee_destination', 'Arrivée à destination'), # Avant déchargement
        ('terminee', 'Terminée (Livrée)'), # Remplacera livree_totalement
        ('probleme_signale', 'Problème signalé'),
        ('annulee', 'Annulée'),
    ]
    statut_livraison = models.CharField(
        max_length=30,
        choices=STATUT_LIVRAISON_CHOICES,
        default='planifiee',
        verbose_name="Statut de la Livraison"
    )
    notes_internes_livraison = models.TextField(blank=True, null=True, verbose_name="Notes Internes")

    def __str__(self):
        return f"Livraison ID {self.id} par {self.chauffeur.user.username if self.chauffeur and hasattr(self.chauffeur, 'user') else 'N/A'}"

    def save(self, *args, **kwargs):
        if self.date_planification_debut and self.duree_estimee_heures:
            hours = float(self.duree_estimee_heures)
            self.date_planification_fin_estimee = self.date_planification_debut + timedelta(hours=hours)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Livraison"
        verbose_name_plural = "Livraisons"
        ordering = ['-date_planification_debut']

class Suivi(models.Model):
    livraison = models.ForeignKey(Livraison, on_delete=models.CASCADE, related_name='evenements_suivi', verbose_name="Livraison Associée")
    timestamp_evenement = models.DateTimeField(default=timezone.now, verbose_name="Horodatage Événement")
    statut_reporte = models.CharField(max_length=100, verbose_name="Statut Reporté")
    localisation_texte = models.CharField(max_length=255, blank=True, null=True, verbose_name="Localisation (Texte)") # Alternative si pas de lat/lon
    # localisation_latitude = models.FloatField(null=True, blank=True) # Si vous voulez stocker la lat/lon
    # localisation_longitude = models.FloatField(null=True, blank=True)
    photo_preuve_url = models.URLField(blank=True, null=True, verbose_name="URL Photo Preuve")
    signature_recepteur_url = models.URLField(blank=True, null=True, verbose_name="URL Signature Récepteur")
    notes_evenement = models.TextField(blank=True, null=True, verbose_name="Notes sur l'Événement")

    def __str__(self):
        return f"Suivi ({self.statut_reporte}) pour Livraison ID {self.livraison.id} à {self.timestamp_evenement.strftime('%d/%m/%y %H:%M')}"

    class Meta:
        verbose_name = "Événement de Suivi"
        verbose_name_plural = "Événements de Suivi"
        ordering = ['-timestamp_evenement']
