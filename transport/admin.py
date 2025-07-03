from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import (
    Client, Chauffeur, GestionnaireLogistique,
    Transporteur, Vehicule,
    Commande, Livraison, Itineraire, Suivi 
)
from django.utils.safestring import mark_safe
from django.utils.html import format_html
class TransporteurCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email', 'first_name', 'last_name')

class TransporteurChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active')

@admin.register(Transporteur)
class TransporteurAdmin(admin.ModelAdmin):
    list_display = ('get_photo_display', 'nom', 'nom_entreprise', 'contact_email', 'contact_telephone', 'user', 'date_inscription')
    search_fields = ('nom', 'nom_entreprise', 'user__username')
    fieldsets = (
        (None, {
            'fields': ('user','photo_profil', 'nom', 'nom_entreprise')
        }),
        ('Coordonnées', {
            'fields': ('adresse', 'contact_email', 'contact_telephone')
        }),
        ('Autres informations', {
            'fields': ('details_contrat', 'date_inscription')
        }),
    )
    readonly_fields = ('date_inscription',)
    

    @admin.display(description='Photo')
    
    def get_photo_display(self, obj):
        if obj.photo_profil:
               return format_html(f'<img src="{obj.photo_profil.url}" width="50" height="50" style="border-radius:50%; object-fit:cover;" />')
        return "Aucune photo"

    def save_model(self, request, obj, form, change):
        if not obj.user_id:  # Si c'est une nouvelle création
            # Créer un nouvel utilisateur
            user = User.objects.create_user(
                username=form.cleaned_data['nom_entreprise'].lower().replace(' ', '_'),
                email=obj.contact_email,
                password='motdepasseparDefaut',  # À changer ou envoyer par email
                first_name=obj.nom.split(' ')[0] if obj.nom else '',
                last_name=' '.join(obj.nom.split(' ')[1:]) if obj.nom else ''
            )
            obj.user = user
        super().save_model(request, obj, form, change)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'adresse_facturation', 'preferences_contact', 'photo_profil_display')
    search_fields = ('user__username', 'user__email')
    
    # Méthode pour afficher la photo
    def photo_profil_display(self, obj):
        if obj.photo_profil:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:50%;" />', 
                obj.photo_profil.url
            )
        return "Aucune photo"
    photo_profil_display.short_description = 'Photo de profil'
    
    # Configuration des champs pour le formulaire d'édition
    fieldsets = (
        (None, {
            'fields': ('user', 'adresse_facturation', 'preferences_contact', 'notes_client')
        }),
        ('Photo de profil', {
            'fields': ('photo_profil',),
            'classes': ('wide',)
        }),
    )

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    list_display = ('user', 'numero_permis', 'disponibilite_statut')
    list_filter = ('disponibilite_statut',)
    search_fields = ('user__username', 'numero_permis')

@admin.register(GestionnaireLogistique)
class GestionnaireLogistiqueAdmin(admin.ModelAdmin):
    list_display = ('user', 'matricule_employe', 'telephone_professionnel')
    search_fields = ('user__username', 'matricule_employe')

@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('immatriculation', 'type_vehicule', 'transporteur', 'statut_vehicule', 'capacite_poids_kg')
    list_filter = ('statut_vehicule', 'type_vehicule', 'transporteur')
    search_fields = ('immatriculation',)

class SuiviInline(admin.TabularInline):
    model = Suivi
    extra = 0
    readonly_fields = ('timestamp_evenement',)

@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_vehicule_immatriculation', 'get_chauffeur_username', 'date_planification_debut', 'statut_livraison')
    list_filter = ('statut_livraison', 'chauffeur', 'vehicule')
    search_fields = ('id', 'chauffeur__user__username', 'vehicule__immatriculation')
    filter_horizontal = ('commandes',)
    inlines = [SuiviInline]
    date_hierarchy = 'date_planification_debut'

    @admin.display(description='Véhicule')
    def get_vehicule_immatriculation(self, obj):
        return obj.vehicule.immatriculation if obj.vehicule else '-'

    @admin.display(description='Chauffeur')
    def get_chauffeur_username(self, obj):
        return obj.chauffeur.user.username if obj.chauffeur else '-'

@admin.register(Itineraire)
class ItineraireAdmin(admin.ModelAdmin):
    list_display = ('id', 'distance_totale_km_estimee', 'get_duree_en_heures_display', 'date_creation')
    readonly_fields = ('date_creation',)

    @admin.display(description="Durée Estimée (heures)", ordering='duree_totale_sec_estimee')
    def get_duree_en_heures_display(self, obj):
        if obj.duree_totale_heures_estimee is not None:
            return f"{obj.duree_totale_heures_estimee:.2f} h"
        return "-"

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    # --- SECTION 1 : AFFICHAGE DANS LA LISTE ---
    # Affiche les colonnes principales dans la liste des commandes.
    # J'ai ajouté 'montant_total' ici pour le voir d'un coup d'œil.
    list_display = (
        'reference_commande',
        'client', # Django affichera le __str__ du modèle Client
        'statut_commande',
        'montant_total',  # CHAMP AJOUTÉ À LA LISTE
        'date_creation',
        'date_souhaitee_livraison',
    )

    # --- SECTION 2 : FILTRES ET RECHERCHE ---
    # Permet de filtrer et rechercher facilement.
    list_filter = (
        'statut_commande',
        'date_creation',
        'date_souhaitee_livraison',
    )
    search_fields = (
        'reference_commande',
        'client__user__username',
        'description_marchandise'
    )
    date_hierarchy = 'date_creation' # Ajoute une navigation par date en haut


    # --- SECTION 3 : FORMULAIRE DE DÉTAIL (le plus important pour votre problème) ---
    # Organise les champs quand on modifie UNE commande.
    # J'ai ajouté 'montant_total' dans la première section.
    fieldsets = (
        ('Informations Principales', {
            'fields': (
                'client',
                'statut_commande',
                'montant_total',  # CHAMP AJOUTÉ AU FORMULAIRE
                'reference_commande', # Souvent en readonly
            )
        }),
        ('Détails de l\'Expédition', {
            'fields': (
                'description_marchandise',
                'poids_kg',
                'volume_m3',
                'instructions_speciales'
            ),
        }),
        ('Adresses et Dates', {
            'fields': (
                'adresse_chargement',
                'adresse_livraison',
                'date_souhaitee_livraison',
                'date_creation', # Souvent en readonly
            )
        }),
        ('Gestion interne (si refus)', {
             'fields': ('motif_annulation',),
             'classes': ('collapse',) # Section repliée par défaut
        })
    )

    # --- SECTION 4 : CHAMPS EN LECTURE SEULE ---
    # Empêche la modification de certains champs auto-générés.
    readonly_fields = (
        'date_creation',
        'reference_commande',
    )

    # Amélioration pour l'affichage du client si vous n'avez pas de 'get_client'
    def get_client_name(self, obj):
        if obj.client and obj.client.user:
            return obj.client.user.get_full_name() or obj.client.user.username
        return "N/A"
    get_client_name.short_description = 'Client'


    @admin.display(description="Client", ordering='client__user__last_name')
    def get_client(self, obj):
        return f"{obj.client.user.get_full_name()}" if obj.client else '-'

    @admin.display(description="Création", ordering='date_creation')
    def date_creation_short(self, obj):
        return obj.date_creation.strftime("%d/%m/%Y")

    @admin.display(description="Livraison souhaitée", ordering='date_souhaitee_livraison')
    def date_souhaitee_livraison_short(self, obj):
        return obj.date_souhaitee_livraison.strftime("%d/%m/%Y")

    @admin.display(description="Poids/Volume")
    def poids_volume_display(self, obj):
        volume = f"{obj.volume_m3} m³" if obj.volume_m3 else "-"
        return f"{obj.poids_kg} kg / {volume}"