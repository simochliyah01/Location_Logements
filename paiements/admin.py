from django.contrib import admin
from .models import Paiement

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ['reference', 'reservation', 'montant', 'methode', 'statut', 'date_paiement']
    list_filter = ['statut', 'methode']
    search_fields = ['reference']