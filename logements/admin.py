from django.contrib import admin
from .models import Logement , Temoignage

@admin.register(Logement)
class LogementAdmin(admin.ModelAdmin):
    list_display = ['titre', 'ville', 'proprietaire', 'prix_par_nuit', 'disponible']
    list_filter = ['disponible', 'type_logement', 'ville']
    search_fields = ['titre', 'ville', 'adresse']
    list_editable = ['disponible']

@admin.register(Temoignage)
class TemoignageAdmin(admin.ModelAdmin):
    list_display = ['auteur', 'note', 'approuve', 'date_creation']
    list_editable = ['approuve']
    list_filter = ['approuve', 'note']