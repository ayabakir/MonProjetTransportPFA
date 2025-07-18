# Generated by Django 5.1.8 on 2025-06-21 22:47

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0003_alter_transporteur_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicule',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Date de création'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vehicule',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Date de mise à jour'),
        ),
    ]
