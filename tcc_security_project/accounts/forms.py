# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User

class CustomUserChangeForm(UserChangeForm):
    password = None 
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

class EmailChangeRequestForm(forms.Form):
    new_email = forms.EmailField(label="Novo endereço de e-mail", required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_new_email(self):
        new_email = self.cleaned_data.get('new_email')
        if not new_email:
            return new_email
            
        # CORREÇÃO CRÍTICA: 'iexact' (não 'ineaxt')
        if User.objects.filter(email__iexact=new_email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("Este endereço de e-mail já está em uso.")
            
        return new_email