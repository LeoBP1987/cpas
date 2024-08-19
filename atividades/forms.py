from typing import Any
from django import forms
from atividades.models import TipoAtividade, Instituicao, Atividades
from calendario.models import Calendario
from datetime import date

class TipoAtividadeForms(forms.ModelForm):
    class Meta:
        model = TipoAtividade
        fields = ['nome_tipo', 'categoria']
        widgets = {
            'nome_tipo': forms.TextInput(attrs={'class':'main-forms__campo_input'}),
            'categoria': forms.TextInput(attrs={'class':'main-forms__campo_input'})
        }

class InstituicaoForms(forms.ModelForm):
    class Meta:
        model = Instituicao
        fields = ['nome_curto', 'nome_inst', 'imagem', 'valor_padrao', 'endereco', 'telefone', 'contato']
        widgets = {
            'nome_curto': forms.TextInput(attrs={'class':'main-forms__campo_input'}),
            'nome_inst': forms.TextInput(attrs={'class':'main-forms__campo_input'}),
            'imagem': forms.FileInput(attrs={'class':'main-forms__campo_input'}),
            'valor_padrao': forms.TextInput(attrs={
                'class':'main-forms__campo_input',
                'id': 'id_valor_inst',
                'type': 'text',
                }),
            'endereco': forms.TextInput(attrs={'class':'main-forms__campo_input'}),
            'telefone': forms.TextInput(attrs={
                'class': 'main-forms__campo_input',
                'placeholder': '(xx) xxxxx-xxxx',
                'id': 'id_tel_inst',
            }),
            'contato': forms.TextInput(attrs={'class':'main-forms__campo_input'})
        }

    def clean_valor_padrao(self):
        valor = self.cleaned_data['valor_padrao']
        if valor is None:
            return None

        # Remove 'R$', vírgulas e espaços extras
        valor = str(valor).replace('R$ ', '').replace(',', '').strip()

        try:
            return valor
        except ValueError:
            # Se não for possível converter, retorne um erro
            raise forms.ValidationError(f'Valor após formatação {valor}')
    
class AtividadesForms(forms.ModelForm):
    extra_param = forms.CharField(max_length=100, required=False)
    class Meta:
        model = Atividades
        exclude = ['cod', 'id_vir']
        fields = ['instituicao', 'tipo_atividade', 'data', 'entrada', 'saida', 'nao_remunerado', 'valor', 'sequencia', 'data_final_seq', 'obs', 'extra_param']
        labels = {
            'nao_remunerado': 'Não Remunerado',
        }
        widgets = {
            'instituicao': forms.Select(attrs={'class':'main-forms__campo_input', 'id':'id_instituicao'}),
            'tipo_atividade': forms.Select(attrs={'class':'main-forms__campo_input'}),
            'data': forms.DateInput(attrs={
                'class':'main-forms__campo_input', 
                'type': 'date',
                'min': date.today().isoformat(),
                'id':'id_data'
                }),
            'entrada': forms.Select(attrs={'class':'main-forms__campo_input', 'id':'id_entrada'}, choices=Atividades.HORAS_ENT),
            'saida': forms.Select(attrs={'class':'main-forms__campo_input', 'id':'id_saida'}, choices=Atividades.HORAS_SAI),
            'nao_remunerado': forms.CheckboxInput(attrs={
                'class':'main-forms__valor_checkbox', 
                'id':'id_nao_remunerado',
                'type': 'checkbox',
                }),
            'valor': forms.TextInput(attrs={'class':'main-forms__campo_input', 'id':'id_valor'}),
            'sequencia' : forms.RadioSelect(attrs={'class':'main-forms__sequencia_radiobox'}, choices=Atividades.SEQUENCIA),
            'data_final_seq': forms.DateInput(attrs={
                'class':'main-forms__campo_input', 
                'type': 'date',
                'id':'id_data_final_seq'
                }),
            'obs': forms.Textarea(attrs={'class':'main-forms__campo_input'})
        }