from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['id', 'logement', 'locataire', 'date_arrivee', 'date_depart', 'statut']
    list_filter = ['statut']
    search_fields = ['logement__titre', 'locataire__username']
    list_editable = ['statut']