from django.db import models
from reservations.models import Reservation

class Paiement(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('paye', 'Payé'),
        ('rembourse', 'Remboursé'),
        ('echoue', 'Échoué'),
    ]
    METHODE_CHOICES = [
        ('carte', 'Carte bancaire'),
        ('virement', 'Virement'),
        ('paypal', 'PayPal'),
    ]
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='paiement')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    methode = models.CharField(max_length=20, choices=METHODE_CHOICES, default='carte')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_paiement = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"Paiement {self.reference} - {self.statut}"