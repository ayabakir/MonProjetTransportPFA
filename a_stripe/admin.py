from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import StripeCustomer, StripePayment

class StripePaymentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'commande', 'statut', 'montant', 'date_creation')
    list_filter = ('statut', 'currency')
    search_fields = ('stripe_payment_intent_id', 'commande__reference_commande')

class StripeCustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'stripe_customer_id', 'created_at')
    search_fields = ('user__username', 'stripe_customer_id')

admin.site.register(StripeCustomer, StripeCustomerAdmin)
admin.site.register(StripePayment, StripePaymentAdmin)