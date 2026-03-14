from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class RegisterForm(UserCreationForm):
    cin = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: AB123456'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'telephone', 'cin', 'role', 'password1', 'password2']

    def clean_cin(self):                          # ← 4 espaces
        cin = self.cleaned_data.get('cin')        # ← 8 espaces
        if cin:                                   # ← 8 espaces
            if User.objects.filter(cin=cin).exists():
                raise forms.ValidationError("Ce CIN est déjà utilisé par un autre compte.")
        return cin

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Nom d\'utilisateur')
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'telephone','cin','avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'cin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: AB123456'}),
        }    
def clean_cin(self):
    cin = self.cleaned_data.get('cin')
    if cin:
        from .models import User
        qs = User.objects.filter(cin=cin)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ce CIN est déjà utilisé par un autre compte.")
    return cin

