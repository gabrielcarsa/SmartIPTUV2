from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.forms import AuthenticationForm

class EmailLoginForm(AuthenticationForm):
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Digite sua senha',
            'class': 'form-control',
            'autocomplete': 'off',
        })
    )
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Digite seu e-mail',
            'autocomplete': 'off',
            'class': 'form-control',
            'autofocus': 'autofocus',
        })
    )

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150, 
        required=True,
        label="Seu nome",
        widget=forms.TextInput(attrs={
            'placeholder': 'Digite seu nome',
            'class': 'form-control',
            'autocomplete': 'off',
            'autofocus': 'autofocus',
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Ex.: exemplo@dominio.com',
            'class': 'form-control',
            'autocomplete': 'off',
            'autofocus': 'autofocus',
        })
    )
    phone = forms.CharField(
        max_length=15, 
        required=True,
        label="Telefone",
        widget=forms.TextInput(attrs={
            'placeholder': 'Digite seu telefone',
            'autocomplete': 'off',
            'class': 'form-control',
            'autofocus': 'autofocus',
        })
    )
        
    class Meta:
        model = User
        fields = ('first_name', 'email', 'phone', 'password1', 'password2')

    def save(self, commit=True):

        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Use e-mail as username

        if commit:
            user.save()

        # Add phone to user
        phone = self.cleaned_data.get('phone')
        if phone:
            Profile.objects.create(user=user, phone=phone)
        else:
            Profile.objects.create(user=user)
        
        return user

