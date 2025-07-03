

from django import forms
from django.contrib.auth.forms import UserCreationForm # Modifié pour utiliser UserCreationForm
from django.contrib.auth.models import User
from .models import Client, Transporteur, Vehicule, Commande, Livraison, Vehicule, Chauffeur
from django.contrib.auth.forms import UserChangeForm 
from .utils import verifier_disponibilite
from django.contrib.auth.forms import UserChangeForm
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Commande, Livraison, Vehicule, Chauffeur
# Assurez-vous que cette fonction existe bien dans un fichier utils.py
from .utils import verifier_disponibilite 

 # Assurez-vous que Livraison est importé

# Formulaire d'inscription pour les Clients
class ClientSignUpForm(UserCreationForm): # Hérite de UserCreationForm pour gérer la création de User
    # Champs spécifiques au profil Client que vous voulez à l'inscription
    adresse_facturation = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), required=False, label="Adresse de Facturation")
    preferences_contact = forms.CharField(max_length=50, required=False, label="Préférences de Contact")
    # Ajoutez first_name, last_name, email si UserCreationForm ne les gère pas comme vous voulez
    # UserCreationForm par défaut gère username, password1, password2
    # Pour ajouter email, first_name, last_name à UserCreationForm, il faut le surcharger un peu plus
    # ou utiliser un formulaire User séparé et un formulaire ClientProfile.
    # Pour la simplicité du PFA, ClientSignUpForm pourrait juste créer le User via UserCreationForm
    # et vous demandez au client de compléter son profil Client plus tard.
    # Ou, vous redéfinissez les champs ici.

    class Meta(UserCreationForm.Meta): # Hérite de la Meta de UserCreationForm
        model = User
        # UserCreationForm inclut username, password1, password2.
        # Si vous voulez first_name, last_name, email directement ici:
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=True) # UserCreationForm.save() gère la création de l'utilisateur et le hachage du mot de passe
        if commit:
            # Crée le profil Client associé
            client_profile = Client.objects.create(
                user=user, # Lie le profil à l'utilisateur créé
                adresse_facturation=self.cleaned_data.get('adresse_facturation', ''),
                preferences_contact=self.cleaned_data.get('preferences_contact', '')
            )
            # Si vous avez ajouté first_name, last_name, email dans Meta.fields
            # ils seront sauvegardés sur l'objet user par super().save()
        return user

# Formulaire d'inscription pour les Transporteurs
class TransporteurSignUpForm(UserCreationForm):
    nom_entreprise = forms.CharField(max_length=200, required=True, label="Nom de l'Entreprise")
    nom_responsable = forms.CharField(max_length=100, required=True, label="Nom du Responsable") # Renommé pour correspondre au modèle
    adresse = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), required=False)
    contact_email_principal = forms.EmailField(required=True, label="Email de Contact Principal") # Renommé pour correspondre au modèle
    contact_telephone = forms.CharField(max_length=20, required=False)
    details_contrat = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email') # first/last name pour le contact

    def save(self, commit=True):
        user = super().save(commit=True)
        user.first_name = self.cleaned_data.get('first_name', '') # Peut être le nom du contact
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email') # Email de connexion du User
        user.save()

        if commit:
            Transporteur.objects.create(
                user=user,
                nom_entreprise=self.cleaned_data['nom_entreprise'],
                nom=self.cleaned_data['nom_responsable'], # Correspond au champ 'nom' du modèle Transporteur
                adresse=self.cleaned_data.get('adresse'),
                contact_email_principal=self.cleaned_data['contact_email_principal'], # Champ 'contact_email' dans le modèle
                contact_telephone=self.cleaned_data.get('contact_telephone'),
                details_contrat=self.cleaned_data.get('details_contrat')
            )
        return user

# Formulaire pour modifier le profil Transporteur (pas l'utilisateur User)
class TransporteurForm(forms.ModelForm):
    class Meta:
        model = Transporteur
        # Exclure 'user' et 'date_inscription' car ils ne devraient pas être modifiés ici
        fields = ['photo_profil','nom_entreprise', 'nom', 'adresse', 'contact_email', 'contact_telephone', 'details_contrat']
        widgets = {
            'nom_entreprise': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'details_contrat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo_profil': forms.FileInput(attrs={'class': 'd-none'}),
        }

# Formulaire pour ajouter/modifier un Véhicule
class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = [
            'immatriculation', 
            'type_vehicule', 
            'capacite_poids_kg', 
            'capacite_volume_m3', 
            'statut_vehicule', 
            'localisation_actuelle', 
            'consommation_moyenne_l_100km'
        ]
        # Le champ 'transporteur' sera assigné automatiquement dans la vue pour l'ajout
        # Pour la modification, il pourrait être affiché en lecture seule ou non modifiable
        widgets = {
            'immatriculation': forms.TextInput(attrs={'placeholder': 'Ex: AA-123-BB'}),
            'type_vehicule': forms.TextInput(attrs={'placeholder': 'Ex: Fourgonnette 12m³'}),
            'statut_vehicule': forms.Select(attrs={'class': 'form-select'}), # Pour appliquer style Bootstrap
            # ... ajoutez des classes Bootstrap via attrs ici ou avec un templatetag ...
        }
        labels = {
            'immatriculation': "Plaque d'Immatriculation",
            'consommation_moyenne_l_100km': "Consommation (L/100km)",
        }

# Formulaire pour créer une Commande
class CommandeForm(forms.ModelForm):
    date_souhaitee_livraison = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), # Ajout de classe Bootstrap
        label="Date Souhaitée de Livraison"
    )

    class Meta:
        model = Commande
        fields = [
            'description_marchandise', 
            'poids_kg', 
            'volume_m3', 
            'adresse_chargement', 
            'adresse_livraison', 
            'date_souhaitee_livraison', 
            'instructions_speciales'
        ]
        widgets = {
            'description_marchandise': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ex: 10 cartons de livres...', 'class': 'form-control'}),
            'poids_kg': forms.NumberInput(attrs={'placeholder': 'Ex: 150.5', 'class': 'form-control'}),
            'volume_m3': forms.NumberInput(attrs={'placeholder': 'Ex: 1.2', 'class': 'form-control'}),
            'adresse_chargement': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Adresse complète pour l\'enlèvement', 'class': 'form-control'}),
            'adresse_livraison': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Adresse complète pour la livraison', 'class': 'form-control'}),
            'instructions_speciales': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Ex: Livraison au 2ème étage...', 'class': 'form-control'}),
        }
        labels = {
            'description_marchandise': "Description de la Marchandise",
            'poids_kg': "Poids Total (kg)",
            'volume_m3': "Volume Total (m³)",
            'adresse_chargement': "Adresse d'Enlèvement",
            'adresse_livraison': "Adresse de Livraison",
            'instructions_speciales': "Instructions Spéciales (optionnel)",
        }

# Formulaires pour les actions du Chauffeur
class AccepterRefuserLivraisonForm(forms.ModelForm):
    acceptee = forms.ChoiceField(
        choices=[(True, 'Accepter la livraison'), (False, 'Refuser la livraison')],
        widget=forms.RadioSelect,
        label="Votre décision pour cette mission :"
    )
    motif_refus_chauffeur = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Si refus, veuillez indiquer la raison ici...'}),
        required=False,
        label="Motif du refus"
    )

    class Meta:
        model = Livraison
        fields = ['motif_refus_chauffeur'] # 'acceptee' n'est pas un champ du modèle, géré en vue

class MajStatutLivraisonForm(forms.ModelForm):
    STATUT_CHOICES_CHAUFFEUR = [
        ('', '---------'), # Option vide
        ('en_cours_chargement', 'Début du chargement'),
        ('en_transit', 'En transit (Marchandise chargée et parti)'),
        # Vous pourriez ajouter des étapes plus spécifiques si nécessaire
        # ex: ('arrive_point_intermediaire', 'Arrivé à un point intermédiaire'),
        ('probleme_signale', 'Problème rencontré (décrire dans la note)'),
        ('terminee', 'Livraison terminée (tous les points desservis)'),
    ]
    nouveau_statut = forms.ChoiceField(
        choices=STATUT_CHOICES_CHAUFFEUR, 
        label="Mettre à jour le statut à",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    derniere_note_chauffeur = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ajoutez une note pour le gestionnaire (ex: détails du problème, confirmation de livraison avec nom du réceptionnaire)...'}),
        required=False,
        label="Note / Informations complémentaires"
    )
    class Meta:
        model = Livraison # Pour lier la note au modèle
        fields = ['derniere_note_chauffeur']

class UserUpdateForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ClientUpdateForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['adresse_facturation', 'preferences_contact', 'photo_profil']
        widgets = {
            'photo_profil': forms.FileInput(attrs={'class': 'd-none', 'id': 'id_photo_profil'}),
        }
# transport/forms.py

# ... (gardez tous les autres formulaires avant celui-ci) ...

# transport/forms.py

# ... (gardez tous les autres formulaires avant celui-ci) ...

class PlanificationLivraisonForm(forms.ModelForm):
    # --- LA CORRECTION EST ICI ---
    # On utilise le widget de l'admin pour le champ 'commandes'
    commandes = forms.ModelMultipleChoiceField(
        queryset=Commande.objects.filter(statut_commande='validee'),
        widget=FilteredSelectMultiple("Commandes", is_stacked=False),
        label="Commandes Associées",
        required=True
    )

    class Meta:
        model = Livraison
        fields = [
            'commandes', 'vehicule', 'chauffeur', 
            'date_planification_debut', 'duree_estimee_heures', 'notes_internes_livraison'
        ]
        widgets = {
            'date_planification_debut': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}, format='%Y-%m-%dT%H:%M'),
            'duree_estimee_heures': forms.NumberInput(attrs={'step': "0.5", 'class': 'form-control'}),
            'notes_internes_livraison': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'vehicule': forms.Select(attrs={'class': 'form-select'}),
            'chauffeur': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'vehicule': "Véhicule à assigner",
            'chauffeur': "Chauffeur à assigner",
            'date_planification_debut': "Date et heure de début de la mission",
            'duree_estimee_heures': "Durée estimée de la mission (heures)",
            'notes_internes_livraison': "Notes internes (optionnel)"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicule'].queryset = Vehicule.objects.filter(statut_vehicule='disponible')
        self.fields['chauffeur'].queryset = Chauffeur.objects.filter(disponibilite_statut='disponible')
        if not self.initial.get('date_planification_debut'):
            self.initial['date_planification_debut'] = timezone.now() + timedelta(hours=1)
        self.fields['vehicule'].empty_label = "Sélectionnez un véhicule..."
        self.fields['chauffeur'].empty_label = "Sélectionnez un chauffeur..."