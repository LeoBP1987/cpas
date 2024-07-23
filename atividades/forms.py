from django import forms
from atividades.models import TipoAtividade, Instituicao, Atividades

class TipoAtividadeForms(forms.ModelForm):
    class Meta:
        model = TipoAtividade
        fields = ['nome_tipo', 'horas']
        widgets = {
            'nome_tipo': forms.TextInput(attrs={'class':'main-forms__campo_input'}),
            'horas': forms.TextInput(attrs={
                'class':'main-forms__campo_input',
                'placeholder': 'Digite apenas números'})
        }

class InstituicaoForms(forms.ModelForm):
    class Meta:
        model = Instituicao
        fields = ['nome_inst', 'imagem', 'valor_padrao', 'endereco', 'telefone', 'contato']
        widgets = {
            'nome_inst': forms.TextInput(attrs={'class':'main-forms__campo_input'}),
            'imagem': forms.FileInput(attrs={'class':'main-forms__campo_input'}),
            'valor_padrao': forms.NumberInput(attrs={'class':'main-forms__campo_input'}),
            'endereco': forms.TextInput(attrs={'class':'main-forms__campo_input'}),
            'telefone': forms.TextInput(attrs={
                'class': 'main-forms__campo_input',
                'placeholder': '(xx) xxxxx-xxxx'
            }),
            'contato': forms.TextInput(attrs={'class':'main-forms__campo_input'})
        }

    def clean_valor_padrao(self):
        valor = self.cleaned_data['valor_padrao']
        if valor is None:
            return None
        valor = str(valor).replace(',', '.')
        return float(valor)