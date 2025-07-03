from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import UserUpdateForm, ClientUpdateForm 
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .forms import (
    ClientSignUpForm, TransporteurSignUpForm, VehiculeForm, CommandeForm,
    TransporteurForm, AccepterRefuserLivraisonForm, MajStatutLivraisonForm, PlanificationLivraisonForm
)
from .models import Client, Transporteur, Vehicule, Commande, Livraison, Chauffeur, Suivi, GestionnaireLogistique, Itineraire
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .routing_services import get_route_from_ors, geocode_address_ors
from django.contrib.auth.views import PasswordChangeView
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.conf import settings
from django.http import JsonResponse
from .utils import verifier_disponibilite 
from datetime import timedelta
from django.db.models import Q
from django.utils import timezone
from .models import Livraison
from django.core.paginator import Paginator
from decimal import Decimal
from django.db.models import F
# Fonctions Utilitaires de Test de Rôle
COMMANDES_MODIFIABLES_OU_SUPPRIMABLES = ['en_attente_validation', 'paiement_en_attente','Validée']
def is_client(user):
    return hasattr(user, 'client')

def is_transporteur(user):
    return hasattr(user, 'transporteur')

def is_chauffeur(user):
    return hasattr(user, 'chauffeur')

def is_gestionnaire(user):
    return hasattr(user, 'gestionnairelogistique')

# Vues d'Inscription
def client_signup_view(request):
    if request.user.is_authenticated:
        return redirect('transport:home')
    if request.method == 'POST':
        form = ClientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Inscription réussie ! Vous êtes maintenant connecté.")
            return redirect('transport:dashboard_client')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = ClientSignUpForm()
    return render(request, 'transport/signup.html', {'form': form})

def transporteur_signup_view(request):
    if request.user.is_authenticated:
        return redirect('transport:home')
    if request.method == 'POST':
        form = TransporteurSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Inscription transporteur réussie ! Vous êtes maintenant connecté.")
            return redirect('transport:dashboard_transporteur')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = TransporteurSignUpForm()
    return render(request, 'transport/signup_transporteur.html', {'form': form})

# Vue de Connexion
def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/admin/')
        if hasattr(request.user, 'client'):
            return redirect('transport:dashboard_client')
        if hasattr(request.user, 'transporteur'):
            return redirect('transport:dashboard_transporteur')
        if hasattr(request.user, 'chauffeur'):
            return redirect('transport:dashboard_chauffeur')
        if hasattr(request.user, 'gestionnairelogistique'):
            return redirect('transport:dashboard_gestionnaire')
        return redirect('transport:home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Bienvenue {user.get_username()} !")
                if user.is_staff:
                    return redirect('/admin/')
                if hasattr(user, 'client'):
                    return redirect('transport:dashboard_client')
                if hasattr(user, 'transporteur'):
                    return redirect('transport:dashboard_transporteur')
                if hasattr(user, 'chauffeur'):
                    return redirect('transport:dashboard_chauffeur')
                if hasattr(user, 'gestionnairelogistique'):
                    return redirect('transport:dashboard_gestionnaire')
                return redirect('transport:home')
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe invalide.")
        else:
            messages.error(request, "Veuillez vérifier vos identifiants.")
    else:
        form = AuthenticationForm()
    return render(request, 'transport/login.html', {'form': form})

# Vue de Déconnexion
@login_required
def logout_view(request):
    """
    Déconnecte l'utilisateur et nettoie les messages de la session
    avant d'ajouter le message de déconnexion.
    """
    # --- LA CORRECTION EST ICI ---
    # 1. On récupère le stockage des messages
    storage = messages.get_messages(request)
    
    # 2. On vide tous les messages actuellement en attente
    # Cela empêche les anciens messages "Bienvenue..." de rester
    for message in storage:
        pass  # Le simple fait de boucler dessus les marque comme "lus"
    storage.used = True # On s'assure qu'ils sont bien effacés

    # 3. On déconnecte l'utilisateur
    logout(request)
    
    # 4. MAINTENANT, on ajoute le nouveau message de déconnexion sur une session propre
    
    # 5. On redirige vers la page de connexion
    return redirect('transport:login') # Rediriger vers login est plus logique

# Tableau de Bord Client
@login_required
@user_passes_test(is_client)
def dashboard_client_view(request):
    client_profile = request.user.client
    commandes_recentes = Commande.objects.filter(client=client_profile).order_by('-date_creation')[:5]
    
    # Statistiques corrigées
    commandes_actives_count = Commande.objects.filter(
        client=client_profile, 
        statut_commande__in=['en_attente_validation', 'validee', 'planifiee', 'en_cours_livraison']
    ).count()
    
    commandes_en_transit_count = Commande.objects.filter(
        client=client_profile, 
        statut_commande='en_cours_livraison'
    ).count()
    
    commandes_en_attente_count = Commande.objects.filter(
        client=client_profile, 
        statut_commande='en_attente_validation'
    ).count()
    
    commandes_total_count = Commande.objects.filter(
        client=client_profile
    ).count()

    context = {
        'commandes_recentes': commandes_recentes,
        'commandes_actives_count': commandes_actives_count,
        'commandes_en_transit_count': commandes_en_transit_count,
        'commandes_en_attente_count': commandes_en_attente_count,
        'commandes_total_count': commandes_total_count,
    }
    return render(request, 'transport/dashboardClient.html', context)


# transport/views.py

# transport/views.py

# ... (gardez vos autres vues)

# REMPLACEZ VOTRE ANCIENNE VUE PAR CELLE-CI :
@login_required
@user_passes_test(is_client)
def ajouter_commande_view(request):
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        if form.is_valid():
            # Ne sauvegarde pas tout de suite, on a besoin des données d'abord
            commande = form.save(commit=False)
            commande.client = request.user.client
            
            # Récupération des données du formulaire
            poids = form.cleaned_data.get('poids_kg')
            adresse_chargement = form.cleaned_data.get('adresse_chargement')
            adresse_livraison = form.cleaned_data.get('adresse_livraison')

            # --- DÉBUT DU CALCUL AUTOMATIQUE ---
            try:
                # 1. Géocoder les adresses
                coords_chargement = geocode_address_ors(adresse_chargement)
                coords_livraison = geocode_address_ors(adresse_livraison)
                
                if not coords_chargement or not coords_livraison:
                    raise ValueError("Une ou plusieurs adresses n'ont pas pu être trouvées. Veuillez vérifier leur orthographe.")

                # 2. Calculer la distance
                route_data = get_route_from_ors([coords_chargement, coords_livraison])
                if not route_data or 'distance_km' not in route_data:
                    raise ValueError("Impossible de calculer un itinéraire entre les deux adresses.")
                
                distance_km = Decimal(str(route_data['distance_km']))

                # 3. Calculer le prix total
                prix_base = Decimal(str(settings.PRIX_BASE))
                prix_par_kg = Decimal(str(settings.PRIX_PAR_KG))
                prix_par_km = Decimal(str(settings.PRIX_PAR_KM))
                montant_calcule = prix_base + (poids * prix_par_kg) + (distance_km * prix_par_km)
                
                # 4. Assigner les valeurs calculées à la commande
                commande.montant_total = montant_calcule.quantize(Decimal('0.01'))
                commande.statut_commande = 'paiement_en_attente'
                message_succes = f"Votre devis est prêt ! Montant total : {commande.montant_total} MAD."

            except Exception as e:
                # Si une erreur se produit (adresse invalide, API en panne...),
                # on sauvegarde la commande sans prix pour un traitement manuel.
                commande.montant_total = None
                commande.statut_commande = 'en_attente_validation'
                message_succes = "Votre commande a été créée, mais le calcul automatique du prix a échoué. Un gestionnaire va la traiter manuellement."
                # Optionnel : logguer l'erreur pour vous
                print(f"Erreur de calcul de devis automatique : {e}")

            # --- FIN DU CALCUL AUTOMATIQUE ---

            # On génère la référence et on sauvegarde
            import uuid
            commande.reference_commande = f"CMD-{timezone.now().strftime('%y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
            commande.save()
            
            messages.success(request, message_succes)
            return redirect('transport:dashboard_client')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = CommandeForm()
        
    return render(request, 'transport/ajouter_commande.html', {'form': form})

    return render(request, 'transport/ajouter_commande.html', {'form': form})
# Tableau de Bord et Gestion Transporteur
# Assurez-vous d'avoir ces imports en haut de votre fichier views.py
from django.utils import timezone
from datetime import timedelta
from django.db.models import F # Nécessaire pour comparer des champs

# ... (gardez vos autres imports)

@login_required
@user_passes_test(is_transporteur)
def dashboard_transporteur(request):
    transporteur = request.user.transporteur
    vehicules = Vehicule.objects.filter(transporteur=transporteur)

    # --- DÉBUT DE LA LOGIQUE D'ACTIVITÉ RÉCENTE ---

    # 1. Définir la période pour les activités "récentes" (ex: les 7 derniers jours)
    sept_jours_avant = timezone.now() - timedelta(days=7)

    # 2. Récupérer les véhicules ajoutés récemment
    vehicules_ajoutes_recemment = Vehicule.objects.filter(
        transporteur=transporteur,
        created_at__gte=sept_jours_avant
    )

    # 3. Récupérer les véhicules modifiés récemment
    # On s'assure que la modification a eu lieu après la création pour éviter les doublons
    vehicules_modifies_recemment = Vehicule.objects.filter(
        transporteur=transporteur,
        updated_at__gte=sept_jours_avant,
        updated_at__gt=F('created_at') + timedelta(seconds=1) # Astuce pour éviter la date de création
    )

    # 4. Créer une liste unifiée d'activités
    activites_brutes = []
    
    # On ajoute les ajouts de véhicules à la liste
    for v in vehicules_ajoutes_recemment:
        activites_brutes.append({
            'type': 'vehicule_ajoute',
            'date': v.created_at,
            'vehicule': v
        })
        
    # On ajoute les modifications de statut à la liste
    for v in vehicules_modifies_recemment:
         activites_brutes.append({
            'type': 'statut_modifie', # Le template gère déjà l'affichage selon le statut actuel
            'date': v.updated_at,
            'vehicule': v
        })

    # 5. Trier la liste par date (du plus récent au plus ancien) et prendre les 5 dernières
    activites_recentes_triees = sorted(
        activites_brutes, 
        key=lambda x: x['date'], 
        reverse=True
    )[:5] # On limite à 5 activités pour ne pas surcharger

    # --- FIN DE LA LOGIQUE D'ACTIVITÉ RÉCENTE ---

    # Contexte mis à jour avec la nouvelle variable
    context = {
        'transporteur': transporteur,
        'vehicules': vehicules,
        'available_vehicles': vehicules.filter(statut_vehicule='disponible').count(),
        'on_mission_vehicles': vehicules.filter(statut_vehicule='en_mission').count(),
        'maintenance_vehicles': vehicules.filter(statut_vehicule='en_maintenance').count(),
        'activites_recentes': activites_recentes_triees, # <--- ON AJOUTE LA VARIABLE ICI
    }
    
    return render(request, 'transport/dashboard.html', context)
@login_required
@user_passes_test(is_transporteur)
def ajouter_vehicule(request):
    if request.method == 'POST':
        form = VehiculeForm(request.POST, request.FILES or None)
        if form.is_valid():
            vehicule = form.save(commit=False)
            vehicule.transporteur = request.user.transporteur
            vehicule.save()
            messages.success(request, "Véhicule ajouté avec succès!")
            return redirect('transport:dashboard_transporteur')
    else:
        form = VehiculeForm()
    return render(request, 'transport/ajouter_vehicule.html', {'form': form})

@login_required
@user_passes_test(is_transporteur)
def modifier_vehicule(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk, transporteur=request.user.transporteur)
    if request.method == 'POST':
        form = VehiculeForm(request.POST, request.FILES or None, instance=vehicule)
        if form.is_valid():
            form.save()
            messages.success(request, "Véhicule modifié avec succès!")
            return redirect('transport:dashboard_transporteur')
    else:
        form = VehiculeForm(instance=vehicule)
    return render(request, 'transport/modifier_vehicule.html', {'form': form, 'vehicule': vehicule})

@login_required
@user_passes_test(is_transporteur)
def supprimer_vehicule(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk, transporteur=request.user.transporteur)
    if request.method == 'POST':
        vehicule.delete()
        messages.success(request, "Véhicule supprimé avec succès!")
        return redirect('transport:dashboard_transporteur')
    return render(request, 'transport/supprimer_vehicule.html', {'vehicule': vehicule})

@login_required
@user_passes_test(is_transporteur)
def modifier_profil_transporteur(request):
    transporteur = get_object_or_404(Transporteur, user=request.user)
    if request.method == 'POST':
        form = TransporteurForm(request.POST, request.FILES, instance=transporteur)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil transporteur mis à jour avec succès!")
            return redirect('transport:dashboard_transporteur')
    else:
        form = TransporteurForm(instance=transporteur)
    return render(request, 'transport/modifier_profil.html', {'form': form})

# Tableau de Bord Chauffeur & Actions
@login_required
@user_passes_test(is_chauffeur)
def dashboard_chauffeur_view(request):
    chauffeur = request.user.chauffeur
    livraisons_a_gerer = Livraison.objects.filter(
        chauffeur=chauffeur,
        statut_livraison__in=['assignee_en_attente_acceptation', 'planifiee', 'en_cours_chargement', 'en_transit', 'probleme_signale']
    ).order_by('date_planification_debut')
    livraisons_terminees_recentes = Livraison.objects.filter(
        chauffeur=chauffeur, statut_livraison='terminee'
    ).order_by('-date_planification_fin_estimee')[:5]

    context = {
        'chauffeur': chauffeur,
        'livraisons_a_gerer': livraisons_a_gerer,
        'livraisons_terminees_recentes': livraisons_terminees_recentes,
        'accepter_refuser_form': AccepterRefuserLivraisonForm(),
        'maj_statut_form': MajStatutLivraisonForm(),
    }
    return render(request, 'transport/dashboard_chauffeur.html', context)

@login_required
@user_passes_test(is_chauffeur)
def action_livraison_chauffeur(request, livraison_id):
    livraison = get_object_or_404(Livraison, id=livraison_id, chauffeur=request.user.chauffeur)
    if request.method == 'POST':
        form = AccepterRefuserLivraisonForm(request.POST)
        if form.is_valid():
            action_acceptee = form.cleaned_data.get('acceptee') == 'True'
            motif = form.cleaned_data.get('motif_refus_chauffeur')

            if action_acceptee:
                livraison.statut_livraison = 'planifiee'
                livraison.motif_refus_chauffeur = ""
                messages.success(request, f"Livraison {livraison.id} acceptée.")
                Suivi.objects.create(livraison=livraison, statut_reporte="Livraison acceptée par le chauffeur")
            else:
                if not motif:
                    messages.error(request, "Le motif est obligatoire si vous refusez la livraison.")
                    return redirect('transport:dashboard_chauffeur')
                livraison.statut_livraison = 'refusee_chauffeur'
                livraison.motif_refus_chauffeur = motif
                messages.warning(request, f"Livraison {livraison.id} refusée.")
                Suivi.objects.create(livraison=livraison, statut_reporte="Livraison refusée par le chauffeur", notes_evenement=f"Motif: {motif}")
            livraison.save()
        else:
            messages.error(request, "Erreur dans le formulaire d'action.")
            for field, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, f"{field}: {error}")
    return redirect('transport:dashboard_chauffeur')

@login_required
@user_passes_test(is_chauffeur)
def maj_statut_livraison_chauffeur(request, livraison_id):
    livraison = get_object_or_404(Livraison, id=livraison_id, chauffeur=request.user.chauffeur)
    if livraison.statut_livraison in ['terminee', 'refusee_chauffeur', 'annulee']:
        messages.warning(request, "Cette livraison ne peut plus être mise à jour.")
        return redirect('transport:dashboard_chauffeur')

    if request.method == 'POST':
        form = MajStatutLivraisonForm(request.POST)
        if form.is_valid():
            nouveau_statut = form.cleaned_data.get('nouveau_statut')
            note = form.cleaned_data.get('derniere_note_chauffeur')

            livraison.statut_livraison = nouveau_statut
            livraison.derniere_note_chauffeur = note
            livraison.date_derniere_maj_chauffeur = timezone.now()
            if nouveau_statut == 'terminee' and not livraison.date_planification_fin_estimee:
                livraison.date_planification_fin_estimee = timezone.now()
            livraison.save()
            
            Suivi.objects.create(
                livraison=livraison, 
                statut_reporte=f"Statut: {livraison.get_statut_livraison_display()}", 
                notes_evenement=f"Note chauffeur: {note if note else 'N/A'}"
            )
            messages.success(request, f"Statut de la livraison {livraison.id} mis à jour.")
        else:
            messages.error(request, "Erreur dans le formulaire de mise à jour.")
            for field, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, f"{field}: {error}")
    return redirect('transport:dashboard_chauffeur')

# Tableau de Bord Gestionnaire Logistique
@login_required
@user_passes_test(is_gestionnaire)
def dashboard_gestionnaire_view(request):
    commandes_a_valider_count = Commande.objects.filter(statut_commande='en_attente_validation').count()
    commandes_validees_non_planifiees_count = Commande.objects.filter(statut_commande='validee').count()
    livraisons_en_cours_count = Livraison.objects.filter(statut_livraison__in=['en_cours_chargement', 'en_transit']).count()
    vehicules_disponibles_count = Vehicule.objects.filter(statut_vehicule='disponible').count()

    dernieres_commandes_a_valider = Commande.objects.filter(statut_commande='en_attente_validation').order_by('-date_creation')[:5]
    dernieres_livraisons_en_cours = Livraison.objects.filter(statut_livraison__in=['en_cours_chargement', 'en_transit']).order_by('-date_planification_debut')[:5]
    notes_recentes = Suivi.objects.exclude(
        notes_evenement__isnull=True
    ).exclude(
        notes_evenement__exact=''
    ).select_related('livraison', 'livraison_chauffeur_user').order_by('-timestamp_evenement')[:5]

    context = {
        'user': request.user,
        'commandes_a_valider_count': commandes_a_valider_count,
        'commandes_validees_non_planifiees_count': commandes_validees_non_planifiees_count,
        'livraisons_en_cours_count': livraisons_en_cours_count,
        'vehicules_disponibles_count': vehicules_disponibles_count,
        'dernieres_commandes_a_valider': dernieres_commandes_a_valider,
        'dernieres_livraisons_en_cours': dernieres_livraisons_en_cours,
        'notes_recentes': notes_recentes,
    }
    return render(request, 'transport/dashboard_gestionnaire.html', context)

@login_required
@user_passes_test(is_gestionnaire)
def liste_commandes_a_valider_view(request):
    commandes = Commande.objects.filter(statut_commande='en_attente_validation').order_by('date_creation')
    context = {'commandes_a_valider': commandes}
    return render(request, 'transport/liste_commandes_a_valider.html', context)

@login_required
@user_passes_test(is_gestionnaire)
def traiter_commande_view(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)

    if commande.statut_commande != 'en_attente_validation':
        messages.warning(request, f"La commande #{commande.reference_commande_or_id()} n'est plus en attente de validation et ne peut être traitée ici.")
        return redirect('transport:liste_commandes_a_valider')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'valider':
            commande.statut_commande = 'paiement_en_attente'
            commande.save()
            messages.success(request, f"La commande #{commande.reference_commande_or_id()} a été validée et est maintenant en attente de paiement par le client.")
        elif action == 'refuser':
            motif_refus = request.POST.get('motif_refus', "Motif non spécifié par le gestionnaire.")
            commande.statut_commande = 'annulee'
            commande.save()
            messages.warning(request, f"La commande #{commande.reference_commande_or_id()} a été refusée.")
        else:
            messages.error(request, "Action non reconnue.")
        return redirect('transport:liste_commandes_a_valider')
    
    return redirect('transport:liste_commandes_a_valider')

# Page d'Accueil
def home_view(request):
    services_data = []
    context = {'services_list': services_data}
    return render(request, 'transport/home.html', context)

# MONPROJETTRANSPORTPFA/transport/views.py
# ... (autres imports)

@login_required
@user_passes_test(is_client)
def profil_client_view(request):
    client = get_object_or_404(Client, user=request.user)
    
    if request.method == 'POST':
        # Instancier les formulaires avec les données POST et les fichiers
        user_form = UserUpdateForm(request.POST, instance=request.user)
        # === CORRECTION PRINCIPALE ICI ===
        client_form = ClientUpdateForm(request.POST, request.FILES, instance=client)
        
        if user_form.is_valid() and client_form.is_valid():
            # La logique de suppression de photo que vous aviez est bonne !
            remove_photo = request.POST.get('remove_photo_profil') == '1'
            if remove_photo and client.photo_profil:
                client.photo_profil.delete(save=False) # Supprime le fichier physique
                client.photo_profil = None # Met le champ à None
            
            user_form.save()
            # client_form.save() est appelé, il prendra en compte le nouveau fichier 
            # de request.FILES ou le champ vidé par client.photo_profil = None.
            client_form.save()
            
            messages.success(request, 'Votre profil a été mis à jour !')
            return redirect('transport:profil_client')
        else:
            # Si les formulaires ne sont pas valides, afficher les erreurs
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
            # Les erreurs spécifiques aux champs seront dans le contexte du formulaire
            # lorsque la page sera ré-affichée.
    else:
        # Pour une requête GET, on affiche les formulaires pré-remplis
        user_form = UserUpdateForm(instance=request.user)
        client_form = ClientUpdateForm(instance=client)
    
    context = {
        'user_form': user_form,
        'client_form': client_form,
        'client': client # client est déjà le profil lié à request.user
    }
    
    return render(request, 'transport/profil_client.html', context)
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Votre mot de passe a été changé avec succès !')
            return redirect('transport:profil_client')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'transport/change_password.html', {
        'form': form
    })
def is_gestionnaire(user):
    return hasattr(user, 'gestionnairelogistique')

# transport/views.py
# ... (imports) ...

from datetime import timedelta
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone
from .forms import PlanificationLivraisonForm
from .models import Commande, Livraison, Itineraire, Vehicule, Chauffeur
from .routing_services import get_route_from_ors, geocode_address_ors
from django.conf import settings

@login_required
@user_passes_test(is_gestionnaire)
def planifier_livraison_view(request):
    # Récupérer les livraisons des prochains jours pour affichage
    date_debut = timezone.now() - timedelta(days=1)
    date_fin = timezone.now() + timedelta(days=7)
    livraisons_prochaines = Livraison.objects.filter(
        date_planification_debut__range=(date_debut, date_fin)
    ).order_by('date_planification_debut')
    
    # Statistiques pour le panneau latéral
    commandes_a_valider_count = Commande.objects.filter(statut_commande='en_attente_validation').count()
    commandes_validees_non_planifiees_count = Commande.objects.filter(statut_commande='validee').count()
    livraisons_en_cours_count = Livraison.objects.filter(statut_livraison__in=['en_cours_chargement', 'en_transit']).count()
    vehicules_disponibles_count = Vehicule.objects.filter(statut_vehicule='disponible').count()

    if request.method == 'POST':
        form = PlanificationLivraisonForm(request.POST)
        if form.is_valid():
            # Récupération des données du formulaire
            commandes_selectionnees = form.cleaned_data['commandes']
            vehicule_selectionne = form.cleaned_data['vehicule']
            chauffeur_selectionne = form.cleaned_data['chauffeur']
            date_debut_planif = form.cleaned_data['date_planification_debut']
            duree_heures = form.cleaned_data.get('duree_estimee_heures', 4.0)
            notes_livraison = form.cleaned_data.get('notes_internes_livraison', '')
            
            # Calcul de la date de fin estimée
            date_fin_estimee = date_debut_planif + timedelta(hours=float(duree_heures))
            
            # Vérification des conflits de réservation
            conflits_vehicule = Livraison.objects.filter(
                vehicule=vehicule_selectionne,
                date_planification_debut__lt=date_fin_estimee,
                date_planification_fin_estimee__gt=date_debut_planif
            ).exists()
            
            conflits_chauffeur = Livraison.objects.filter(
                chauffeur=chauffeur_selectionne,
                date_planification_debut__lt=date_fin_estimee,
                date_planification_fin_estimee__gt=date_debut_planif
            ).exists()
            
            if conflits_vehicule or conflits_chauffeur:
                message_erreur = "Conflit de réservation détecté : "
                if conflits_vehicule:
                    message_erreur += f"Le véhicule {vehicule_selectionne} est déjà réservé. "
                if conflits_chauffeur:
                    message_erreur += f"Le chauffeur {chauffeur_selectionne} est déjà réservé. "
                
                messages.error(request, message_erreur)
                context = {
                    'form': form,
                    'page_title': "Planifier une Nouvelle Livraison",
                    'livraisons_prochaines': livraisons_prochaines,
                    'commandes_a_valider_count': commandes_a_valider_count,
                    'commandes_validees_non_planifiees_count': commandes_validees_non_planifiees_count,
                    'livraisons_en_cours_count': livraisons_en_cours_count,
                    'vehicules_disponibles_count': vehicules_disponibles_count,
                    'conflits': True,
                    'vehicule_conflit': conflits_vehicule,
                    'chauffeur_conflit': conflits_chauffeur
                }
                return render(request, 'transport/planifier_livraison_form.html', context)

            # Géocodage et calcul d'itinéraire
            adresse_depot_config = getattr(settings, 'ADRESSE_DEPOT_PRINCIPAL', "Casablanca, Maroc")
            points_ordonnes_pour_ors = []
            points_etapes_texte = []

            # Point de départ : Dépôt
            coords_depot = geocode_address_ors(adresse_depot_config)
            if coords_depot:
                points_ordonnes_pour_ors.append(coords_depot)
                points_etapes_texte.append(f"DEPART: {adresse_depot_config}")
            else:
                messages.error(request, f"Impossible de géocoder l'adresse du dépôt: '{adresse_depot_config}'")
                return render(request, 'transport/planifier_livraison_form.html', {
                    'form': form, 
                    'page_title': "Planifier une Nouvelle Livraison",
                    'livraisons_prochaines': livraisons_prochaines,
                    'commandes_a_valider_count': commandes_a_valider_count,
                    'commandes_validees_non_planifiees_count': commandes_validees_non_planifiees_count,
                    'livraisons_en_cours_count': livraisons_en_cours_count,
                    'vehicules_disponibles_count': vehicules_disponibles_count,
                })

            # Points de chargement et livraison
            for cmd in commandes_selectionnees.order_by('date_souhaitee_livraison'):
                # Chargement
                coords_chargement = geocode_address_ors(cmd.adresse_chargement)
                if coords_chargement:
                    points_ordonnes_pour_ors.append(coords_chargement)
                    points_etapes_texte.append(f"CHARGEMENT (Cde #{cmd.reference_commande_or_id()}): {cmd.adresse_chargement}")
                else:
                    messages.error(request, f"Impossible de géocoder l'adresse de chargement '{cmd.adresse_chargement}' pour la Commande #{cmd.reference_commande_or_id()}")
                    return render(request, 'transport/planifier_livraison_form.html', {
                        'form': form, 
                        'page_title': "Planifier une Nouvelle Livraison",
                        'livraisons_prochaines': livraisons_prochaines,
                        'commandes_a_valider_count': commandes_a_valider_count,
                        'commandes_validees_non_planifiees_count': commandes_validees_non_planifiees_count,
                        'livraisons_en_cours_count': livraisons_en_cours_count,
                        'vehicules_disponibles_count': vehicules_disponibles_count,
                    })
                
                # Livraison
                coords_livraison = geocode_address_ors(cmd.adresse_livraison)
                if coords_livraison:
                    points_ordonnes_pour_ors.append(coords_livraison)
                    points_etapes_texte.append(f"LIVRAISON (Cde #{cmd.reference_commande_or_id()}): {cmd.adresse_livraison}")
                else:
                    messages.error(request, f"Impossible de géocoder l'adresse de livraison '{cmd.adresse_livraison}' pour la Commande #{cmd.reference_commande_or_id()}")
                    return render(request, 'transport/planifier_livraison_form.html', {
                        'form': form, 
                        'page_title': "Planifier une Nouvelle Livraison",
                        'livraisons_prochaines': livraisons_prochaines,
                        'commandes_a_valider_count': commandes_a_valider_count,
                        'commandes_validees_non_planifiees_count': commandes_validees_non_planifiees_count,
                        'livraisons_en_cours_count': livraisons_en_cours_count,
                        'vehicules_disponibles_count': vehicules_disponibles_count,
                    })

            # Point de retour : Dépôt
            if points_ordonnes_pour_ors and points_ordonnes_pour_ors[-1] != coords_depot:
                points_ordonnes_pour_ors.append(coords_depot)
                points_etapes_texte.append(f"RETOUR: {adresse_depot_config}")

            # Calcul de l'itinéraire
            route_data = get_route_from_ors(points_ordonnes_pour_ors, profile='driving-car')
            if not route_data:
                messages.error(request, "Erreur lors du calcul de l'itinéraire. Veuillez réessayer ou vérifier les adresses.")
                return render(request, 'transport/planifier_livraison_form.html', {
                    'form': form, 
                    'page_title': "Planifier une Nouvelle Livraison",
                    'livraisons_prochaines': livraisons_prochaines,
                    'commandes_a_valider_count': commandes_a_valider_count,
                    'commandes_validees_non_planifiees_count': commandes_validees_non_planifiees_count,
                    'livraisons_en_cours_count': livraisons_en_cours_count,
                    'vehicules_disponibles_count': vehicules_disponibles_count,
                })

            # Création de l'itinéraire
            itineraire = Itineraire.objects.create(
                geometry_geojson=route_data.get('geometry_geojson'),
                points_etapes_str="\n".join(points_etapes_texte),
                distance_totale_km_estimee=route_data.get('distance_km'),
                duree_totale_sec_estimee=route_data.get('duration_sec'),
                instructions_textuelles=route_data.get('instructions_text'),
                raw_ors_response=route_data.get('raw_response')
            )

            # Création de la livraison
            livraison = Livraison.objects.create(
                vehicule=vehicule_selectionne,
                chauffeur=chauffeur_selectionne,
                itineraire=itineraire,
                date_planification_debut=date_debut_planif,
                date_planification_fin_estimee=date_fin_estimee,
                duree_estimee_heures=duree_heures,
                notes_internes_livraison=notes_livraison,
                statut_livraison='assignee_en_attente_acceptation'
            )
            livraison.commandes.set(commandes_selectionnees)

            # Mise à jour des statuts
            for cmd in commandes_selectionnees:
                cmd.statut_commande = 'planifiee'
                cmd.save()
            
            vehicule_selectionne.statut_vehicule = 'en_mission'
            vehicule_selectionne.save()
            
            chauffeur_selectionne.disponibilite_statut = 'en_mission'
            chauffeur_selectionne.save()

            messages.success(request, f"Livraison #{livraison.id} planifiée avec succès !")
            return redirect('transport:dashboard_gestionnaire')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = PlanificationLivraisonForm()
    
    context = {
        'form': form,
        'page_title': "Planifier une Nouvelle Livraison",
        'livraisons_prochaines': livraisons_prochaines,
        'commandes_a_valider_count': commandes_a_valider_count,
        'commandes_validees_non_planifiees_count': commandes_validees_non_planifiees_count,
        'livraisons_en_cours_count': livraisons_en_cours_count,
        'vehicules_disponibles_count': vehicules_disponibles_count,
    }
    return render(request, 'transport/planifier_livraison_form.html', context)



@login_required
@user_passes_test(is_chauffeur)
def api_itineraire_livraison(request, livraison_id):
    print(f"[API] Demande d'itinéraire pour livraison ID: {livraison_id}")
    
    try:
        livraison = Livraison.objects.select_related('itineraire').get(
            id=livraison_id,
            chauffeur=request.user.chauffeur
        )
        print(f"[API] Livraison trouvée: {livraison.id}")
    except Livraison.DoesNotExist:
        print(f"[API] Livraison non trouvée ou accès non autorisé")
        return JsonResponse({'error': 'Livraison non trouvée ou accès non autorisé'}, status=404)
    
    if not livraison.itineraire:
        print("[API] Aucun itinéraire associé")
        return JsonResponse({'error': 'Aucun itinéraire disponible'}, status=404)
    
    itineraire = livraison.itineraire
    response_data = {
        'coordinates': [],
        'points_etapes': [],
        'instructions': itineraire.instructions_textuelles or "Aucune instruction disponible"
    }
    
    # 1. Essayer d'extraire les coordonnées de geometry_geojson
    if itineraire.geometry_geojson:
        print("[API] Tentative d'extraction depuis geometry_geojson")
        try:
            # Structure GeoJSON standard
            if itineraire.geometry_geojson.get('type') == 'LineString':
                response_data['coordinates'] = itineraire.geometry_geojson.get('coordinates', [])
            # Structure de réponse ORS directe
            elif itineraire.geometry_geojson.get('features'):
                feature = itineraire.geometry_geojson['features'][0]
                if feature['geometry']['type'] == 'LineString':
                    response_data['coordinates'] = feature['geometry']['coordinates']
        except Exception as e:
            print(f"[API] Erreur extraction geometry_geojson: {str(e)}")
    
    # 2. Si pas de coordonnées, essayer depuis raw_ors_response
    if not response_data['coordinates'] and itineraire.raw_ors_response:
        print("[API] Tentative d'extraction depuis raw_ors_response")
        try:
            raw_data = itineraire.raw_ors_response
            if raw_data.get('features'):
                feature = raw_data['features'][0]
                if feature['geometry']['type'] == 'LineString':
                    response_data['coordinates'] = feature['geometry']['coordinates']
        except Exception as e:
            print(f"[API] Erreur extraction raw_ors_response: {str(e)}")
    
    # 3. Points d'étape
    if itineraire.points_etapes_str:
        print("[API] Extraction des points d'étape")
        try:
            points = itineraire.points_etapes_str.split('\n')
            for point in points:
                if point:
                    response_data['points_etapes'].append({
                        'label': point,
                        'lat': 0,
                        'lon': 0
                    })
        except Exception as e:
            print(f"[API] Erreur extraction points: {str(e)}")
    
    print(f"[API] Réponse préparée avec {len(response_data['coordinates'])} coordonnées")
    return JsonResponse(response_data)

@login_required
@user_passes_test(is_client)
def mes_commandes_view(request): # Cette vue semble correcte
    client_profile = request.user.client
    commandes_list = Commande.objects.filter(client=client_profile).order_by('-date_creation')
    
    # ... (votre logique de Paginator) ...
    from django.core.paginator import Paginator # Assurez-vous que Paginator est importé
    paginator = Paginator(commandes_list, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'commandes': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'page_title': "Toutes mes commandes"
    }
    return render(request, 'transport/mes_commandes.html', context)


@login_required
@user_passes_test(is_client)
def modifier_commande_view(request, pk):
    commande = get_object_or_404(Commande, id=pk, client=request.user.client)
    
    # === LA CORRECTION EST ICI ===
    # On utilise la propriété du modèle, c'est plus propre !
    if not commande.is_modifiable_ou_supprimable:
        messages.warning(request, f"La commande #{commande.reference_commande_or_id()} ne peut plus être modifiée.")
        return redirect('transport:mes_commandes')
    
    if request.method == 'POST':
        form = CommandeForm(request.POST, instance=commande)
        if form.is_valid():
            # Recalculer le prix si le poids a changé
            poids = form.cleaned_data.get('poids_kg')
            prix_par_kg = settings.PRIX_PAR_KG_DEFAUT
            commande_instance = form.save(commit=False)
            if poids and prix_par_kg:
                commande_instance.montant_total = poids * Decimal(str(prix_par_kg))
            
            commande_instance.save()
            messages.success(request, f"Commande #{commande_instance.reference_commande_or_id()} mise à jour avec succès !")
            return redirect('transport:mes_commandes')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = CommandeForm(instance=commande)
    
    context = {
        'form': form,
        'commande': commande,
    }
    return render(request, 'transport/modifier_commande.html', context)


@login_required
@user_passes_test(is_client)
def supprimer_commande_view(request, pk):
    commande = get_object_or_404(Commande, id=pk, client=request.user.client)
    
    # === LA CORRECTION EST ICI ===
    # On utilise la même propriété ici
    if not commande.is_modifiable_ou_supprimable:
        messages.warning(request, f"La commande #{commande.reference_commande_or_id()} ne peut plus être supprimée.")
        return redirect('transport:mes_commandes')
    
    if request.method == 'POST':
        ref_commande = commande.reference_commande_or_id()
        commande.delete()
        messages.success(request, f"La commande #{ref_commande} a été supprimée avec succès.")
        return redirect('transport:mes_commandes')
    
    context = {
        'commande': commande
    }
    return render(request, 'transport/supprimer_commande.html', context)


@login_required
def commande_detail(request, pk):
    """
    Vue détaillée d'une commande avec suivi et informations complètes
    """
    try:
        # Vérifier que l'utilisateur est bien un client
        client = request.user.client
    except Client.DoesNotExist:
        messages.error(request, "Accès réservé aux clients.")
        return redirect('transport:home')

    try:
        # Récupérer la commande avec vérification de propriété
        commande = get_object_or_404(Commande, pk=pk, client=client)
        
        # Récupérer les événements de suivi si la commande est en cours
        suivi_events = []
        livraison = None
        
        if commande.livraisons.exists():
            livraison = commande.livraisons.first()
            suivi_events = Suivi.objects.filter(
                livraison=livraison
            ).order_by('-timestamp_evenement')
        
        # Préparer les données pour le template
        context = {
            'commande': commande,
            'livraison': livraison,
            'suivi_events': suivi_events,
            'page_title': f"Détails de la commande {commande.reference_commande_or_id}",
            'can_modify': commande.is_modifiable_ou_supprimable,
        }
        
        return render(request, 'transport/detail_commande.html', context)
        
    except Exception as e:
        # Loguer l'erreur pour le débogage
        import logging
        logger = logging.getLogger(_name_)
        logger.error(f"Erreur dans detail_commande: {str(e)}")
        
        messages.error(request, "Une erreur est survenue lors de l'accès aux détails de la commande.")
        return redirect('transport:mes_commandes')
# ---------------------------------------------------
@login_required
@user_passes_test(is_client)
def profil_client_view(request):
    client = get_object_or_404(Client, user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        client_form = ClientUpdateForm(request.POST, request.FILES, instance=client)
        
        if user_form.is_valid() and client_form.is_valid():
            user_form.save()
            client_form.save()
            messages.success(request, 'Votre profil a été mis à jour !')
            return redirect('transport:profil_client')
    else:
        user_form = UserUpdateForm(instance=request.user)
        client_form = ClientUpdateForm(instance=client)
    
    context = {
        'user_form': user_form,
        'client_form': client_form,
        'client': client
    }
    
    return render(request, 'transport/profil_client.html', context)