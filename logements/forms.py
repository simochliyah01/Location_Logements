from django import forms
from .models import Logement

class LogementForm(forms.ModelForm):
    class Meta:
        model = Logement
        fields = ['titre', 'description', 'type_logement', 'adresse', 'ville', 'prix_par_nuit', 'capacite', 'disponible', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }