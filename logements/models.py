from django.db import models
from accounts.models import User


class Logement(models.Model):
    TYPE_CHOICES = [
        ('appartement', 'Appartement'),
        ('maison', 'Maison'),
        ('villa', 'Villa'),
        ('bureau', 'Bureau'),
        ('riad', 'Riad'),
        ('studio', 'Studio'),
    ]
    proprietaire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logements')
    titre = models.CharField(max_length=200)
    description = models.TextField()
    type_logement = models.CharField(max_length=50, choices=TYPE_CHOICES, default='appartement')
    adresse = models.CharField(max_length=300)
    ville = models.CharField(max_length=100)
    prix_par_nuit = models.DecimalField(max_digits=10, decimal_places=2)
    capacite = models.IntegerField(default=1)
    disponible = models.BooleanField(default=True)
    image = models.ImageField(upload_to='logements/', blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre


class Temoignage(models.Model):
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    contenu = models.TextField(max_length=500)
    note = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    date_creation = models.DateTimeField(auto_now_add=True)
    approuve = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.auteur.username} - {self.note}"

class Avis(models.Model):
    logement = models.ForeignKey(Logement, on_delete=models.CASCADE, related_name='avis')
    auteur = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    note = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    commentaire = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['logement', 'auteur']  # Un avis par logement par user

    def __str__(self):
        return f"{self.auteur.username} — {self.logement.titre} ({self.note}★)"