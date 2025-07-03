# transport/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views 

app_name = 'transport'

urlpatterns = [
    # Authentification & Inscription
    path('', views.home_view, name='home'),
    path('signup/client/', views.client_signup_view, name='signup_client'),
    path('signup/transporteur/', views.transporteur_signup_view, name='signup_transporteur'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Tableau de Bord Client
    path('dashboard/client/', views.dashboard_client_view, name='dashboard_client'),
    path('commande/ajouter/', views.ajouter_commande_view, name='ajouter_commande'),
    path('client/profil/', views.profil_client_view, name='profil_client'),

    # Tableau de Bord Transporteur
    path('dashboard/transporteur/', views.dashboard_transporteur, name='dashboard_transporteur'),
    # ### CORRECTION : Ligne en double supprimée ###
    path('transporteur/profil/modifier/', views.modifier_profil_transporteur, name='modifier_profil'),
    path('transporteur/vehicule/ajouter/', views.ajouter_vehicule, name='ajouter_vehicule'),
    path('transporteur/vehicule/modifier/<int:pk>/', views.modifier_vehicule, name='modifier_vehicule'),
    path('transporteur/vehicule/supprimer/<int:pk>/', views.supprimer_vehicule, name='supprimer_vehicule'),

    # Tableau de Bord Chauffeur & Actions
    path('dashboard/chauffeur/', views.dashboard_chauffeur_view, name='dashboard_chauffeur'),
    path('livraison/<int:livraison_id>/action/', views.action_livraison_chauffeur, name='action_livraison_chauffeur'),
    path('livraison/<int:livraison_id>/maj_statut/', views.maj_statut_livraison_chauffeur, name='maj_statut_livraison_chauffeur'),

    # Tableau de Bord Gestionnaire Logistique
    path('gestionnaire/dashboard/', views.dashboard_gestionnaire_view, name='dashboard_gestionnaire'),
    path('commandes-a-valider/', views.liste_commandes_a_valider_view, name='liste_commandes_a_valider'),
    path('gestionnaire/commande/<int:commande_id>/traiter/', views.traiter_commande_view, name='traiter_commande'),
    path('gestionnaire/livraison/planifier/', views.planifier_livraison_view, name='planifier_livraison'),

    # Changement de mot de passe
    # ### CORRECTION : Lignes en double et conflictuelles supprimées ###
    path('password_change/', views.change_password, name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='transport/password_change_done.html'), name='password_change_done'),

    # API & Commandes client
    path('transport/api/livraison/<int:livraison_id>/itineraire/', views.api_itineraire_livraison,  name='api_itineraire_livraison'),
    path('mes-commandes/', views.mes_commandes_view, name='mes_commandes'),
    path('mes-commandes/<int:pk>/modifier/', views.modifier_commande_view, name='modifier_commande'),
    path('mes-commandes/<int:pk>/supprimer/', views.supprimer_commande_view, name='supprimer_commande'),
    path('mes-commandes/<int:pk>/', views.commande_detail, name='commande_detail'),
]