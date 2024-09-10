from typing import Any
from django import forms
from atividades.models import TipoAtividade, Instituicao, Atividades, Categoria, Preferencias
from calendario.models import Calendario
from datetime import date

class CategoriaForms(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome_categoria']
        widgets = {
            'nome_categoria': forms.TextInput(attrs={'class':'main-forms__campo_input'}),
        }

def listar_categorias():
    lista_categorias = []

    categorias = Categoria.objects.all()

    for categoria in categorias:
        lista_categorias.append((categoria.nome_categoria, categoria.nome_categoria))

    return lista_categorias

lista_categorias = listar_categorias()

class TipoAtividadeForms(forms.ModelForm):
    class Meta:
        model = TipoAtividade
        fields = ['nome_tipo', 'categoria']
        widgets = {
            'nome_tipo': forms.TextInput(attrs={'class':'main-forms__campo_input'}),
            'categoria': forms.Select(attrs={'class':'main-forms__campo_input'}, choices=lista_categorias),
        }

class InstituicaoForms(forms.ModelForm):
    class Meta:
        model = Instituicao
        exclude = ['cod_fixo',]
        fields = ['nome_curto', 'nome_inst', 'imagem', 'fixo_mensal_inst', 'valor_fixo', 'endereco', 'telefone', 'contato']
        labels = {
            'nome_curto': 'Nome Curto',
            'nome_inst': 'Nome da Instituição',
            'imagem': 'Imagem',
            'fixo_mensal_inst': 'Fixo Mensal',
            'valor_fixo': 'Valor',
            'endereco': 'Endereço',
            'telefone': 'Telefone',
            'contato': 'Contato'
        }
        widgets = {
            'nome_curto': forms.TextInput(attrs={'class':'main-forms__campo_input'}),
            'nome_inst': forms.TextInput(attrs={'class':'main-forms__campo_input'}),
            'imagem': forms.FileInput(attrs={'class':'main-forms__campo_input'}),
            'fixo_mensal_inst': forms.CheckboxInput(attrs={
                'class':'main-forms__valor_checkbox', 
                'id':'id_fixo_mensal_inst',
                'type': 'checkbox',
                }),
            'valor_fixo': forms.TextInput(attrs={
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

    def clean_valor_fixo(self):
        valor = self.cleaned_data['valor_fixo']
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
    seq_perso = forms.MultipleChoiceField(choices=Atividades.SEQ_PERSO,
                                            widget=forms.CheckboxSelectMultiple(attrs={
                                                'id':'id_seqPersoValue',
                                                'name':'seq_perso'}),
                                            required=False)
    class Meta:
        model = Atividades
        exclude = ['cod', 'id_vir', 'cod_fixo_ativ', 'seq_personalizada']
        fields = ['instituicao', 'tipo_atividade', 'data', 'entrada', 'saida', 'nao_remunerado', 'fixo_mensal_ativ', 'valor', 'sequencia', 'data_final_seq', 'obs', 'extra_param']
        labels = {
            'instituicao': 'Instituição',
            'tipo_atividade': 'Tipo de Atividade',
            'saida': 'Saída',
            'nao_remunerado': 'Não Remunerado',
            'fixo_mensal_ativ': 'Fixo Mensal',
            'data_final_seq': 'Data Final',
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
            'fixo_mensal_ativ': forms.CheckboxInput(attrs={
                'class':'main-forms__valor_checkbox', 
                'id':'id_fixo_mensal_ativ',
                'type': 'checkbox',
                }), 
            'valor': forms.TextInput(attrs={'class':'main-forms__campo_input', 'id':'id_valor'}),
            'sequencia' : forms.RadioSelect(choices=Atividades.SEQUENCIA),
            'data_final_seq': forms.DateInput(attrs={
                'class':'main-forms__campo_input', 
                'type': 'date',
                'id':'id_data_final_seq'
                }),
            'obs': forms.Textarea(attrs={'class':'main-forms__campo_input'})
        }

tipos_graficos = [
    ('bar', 'Barras'),
    ('pie', 'Pizza'),
    ('doughnut', 'Roscas')
]

SEMANA = [
        (0, 'Segunda-Feira'),
        (1, 'Domingo'),
        (2, 'Sábado'),
        (3, 'Sexta-Feira'),
        (4, 'Quinta-Feira'),
        (5, 'Quarta-Feira'),
        (6, 'Terça-Feira')
    ]

class PreferenciasForms(forms.ModelForm):
    class Meta:
        model = Preferencias
        fields = ['horas_sono', 'tipo_grafico', 'inicio_semana', 'hora_envio_tarefas']
        labels = {
            'horas_sono': 'Horas de sono ideais',
            'tipo_grafico': 'Tipo de Gráfico',
            'inicio_semana': 'Semana deve iniciar em:',
            'hora_envio_tarefas': 'Horário de envio das tarefas diárias'
        }
        
        widgets =  {
            'horas_sono': forms.TextInput(attrs={'class':'main-forms__campo_input'}),
            'tipo_grafico': forms.Select(attrs={'class':'main-forms__campo_input'}, choices=tipos_graficos),
            'inicio_semana': forms.Select(attrs={'class':'main-forms__campo_input'}, choices=SEMANA),
            'hora_envio_tarefas': forms.TimeInput(attrs={'class':'main-forms__campo_input', 
                                                         'type':'time', 
                                                         'id': 'idHoraEnvio',
                                                        }),
        }