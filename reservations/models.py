from django.db import models
from accounts.models import User
from logements.models import Logement

class Reservation(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('annulee', 'Annulée'),
        ('terminee', 'Terminée'),
    ]
    locataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    logement = models.ForeignKey(Logement, on_delete=models.CASCADE, related_name='reservations')
    date_arrivee = models.DateField()
    date_depart = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_reservation = models.DateTimeField(auto_now_add=True)

    @property
    def nombre_nuits(self):
        return (self.date_depart - self.date_arrivee).days

    @property
    def prix_total(self):
        return self.nombre_nuits * self.logement.prix_par_nuit

    def __str__(self):
        return f"Réservation {self.id} - {self.locataire} - {self.logement}"