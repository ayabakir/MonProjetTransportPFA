# Generated by Django 5.2 on 2025-06-25 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0007_delete_paiement'),
    ]

    operations = [
        migrations.AddField(
            model_name='commande',
            name='montant_total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Montant Total (MAD)'),
        ),
        migrations.AlterField(
            model_name='commande',
            name='statut_commande',
            field=models.CharField(choices=[('en_attente_validation', 'En attente de validation'), ('validee', 'Validée'), ('paiement_en_attente', 'Paiement en attente'), ('planifiee', 'Planifiée'), ('en_cours_livraison', 'En cours de livraison'), ('livree', 'Livrée'), ('annulee', 'Annulée')], default='en_attente_validation', max_length=30, verbose_name='Statut de la Commande'),
        ),
    ]
