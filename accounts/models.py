from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('locataire', 'Locataire'),
        ('proprietaire', 'Propriétaire'),
        ('admin', 'Administrateur'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='locataire')
    telephone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    cin = models.CharField(max_length=20, blank=True, null=True,unique=True, verbose_name="CIN")

    def is_proprietaire(self):
        return self.role == 'proprietaire'

    def is_locataire(self):
        return self.role == 'locataire'

    def __str__(self):
        return f"{self.username} ({self.role})"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('nouvelle_reservation', 'Nouvelle réservation'),
        ('reservation_confirmee', 'Réservation confirmée'),
        ('reservation_refusee', 'Réservation refusée'),
        ('info', 'Information'),
    ]
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    titre = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    type_notif = models.CharField(max_length=50, choices=TYPE_CHOICES, default='info')
    url = models.CharField(max_length=200, default='/')
    icon = models.CharField(max_length=50, default='fas fa-bell')
    color = models.CharField(max_length=50, default='rgba(124,111,247,0.5)')
    lue = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.destinataire.username} - {self.titre}"