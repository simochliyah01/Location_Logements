from django import forms
from .models import Reservation
from django.core.exceptions import ValidationError
import datetime

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['date_arrivee', 'date_depart']
        widgets = {
            'date_arrivee': forms.DateInput(attrs={'type': 'date'}),
            'date_depart': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_arrivee = cleaned_data.get('date_arrivee')
        date_depart = cleaned_data.get('date_depart')
        if date_arrivee and date_depart:
            if date_arrivee < datetime.date.today():
                raise ValidationError("La date d'arrivée ne peut pas être dans le passé.")
            if date_depart <= date_arrivee:
                raise ValidationError("La date de départ doit être après la date d'arrivée.")
        return cleaned_data