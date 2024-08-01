from typing import Any
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.shortcuts import redirect

class LoginForms(forms.Form):
    nome_login = forms.CharField(
        label='E-mail',
        required=True,
        max_length=100,
        widget = forms.TextInput(
                                        attrs={
                                            'class':'main-forms__campo_input',
                                            'placeholder':'Ex.: João Silva'
                                        }
                                    )
    )
    senha = forms.CharField(
        label='Senha',
        required=True,
        max_length=30,
        widget = forms.PasswordInput(
                                        attrs={
                                            'class':'main-forms__campo_input',
                                            'placeholder':'Digite sua senha',
                                        }
                                    )
    )

class AlterarSenhaForms(forms.Form):
    senha = forms.CharField(
        label='Senha',
        required=True,
        max_length=30,
        widget = forms.PasswordInput(
                                        attrs={
                                            'class':'main-forms__campo_input',
                                            'placeholder':'Digite sua senha',
                                        }
                                    )
    )

    confirmar_senha = forms.CharField(
        label='Confirmar Senha',
        required=True,
        max_length=30,
        widget = forms.PasswordInput(
                                        attrs={
                                            'class':'main-forms__campo_input',
                                            'placeholder':'Confirme sua senha',
                                        }
                                    )
    )

    def clean_confirmar_senha(self):
        senha = self.cleaned_data.get('senha')
        confirmar_senha = self.cleaned_data.get('confirmar_senha')

        if senha and confirmar_senha:
            if senha != confirmar_senha:
                raise forms.ValidationError('As senhas digitadas não são iguais')
            else:
                return senha
            
class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'main-forms__campo_input',
        })

class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomSetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'class': 'main-forms__campo_input',
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'main-forms__campo_input',
        })

        self.fields['new_password2'].help_text = self.fields['new_password1'].help_text 
        self.fields['new_password1'].help_text = ''
        