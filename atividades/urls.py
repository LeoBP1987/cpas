from django.urls import path
from atividades.views import index, novo_tipo, nova_instituicao, nova_atividade, get_valor_fixo, \
                            tipos, editar_tipo, deletar_tipo, instituicoes, editar_instituicao, \
                            deletar_instituicao, editar_atividade, deletar_atividade, deletar_sequencia, \
                            atividade, instituicao, financeiro, rotina, atualizar_financeiro, atualizar_grafico, \
                            atualizar_rotina, atualizar_grafico_rotina

urlpatterns = [
    path('', index, name='index'),
    path('tipos/', tipos, name='tipos'),
    path('novo_tipo/', novo_tipo, name='novo_tipo'),
    path('editar_tipo/<int:tipo_id>', editar_tipo, name='editar_tipo'),
    path('deletar_tipo/<int:tipo_id>', deletar_tipo, name='deletar_tipo'),
    path('instituicoes/', instituicoes, name='instituicoes'),
    path('editar_instituicao/<int:id_inst>', editar_instituicao, name='editar_instituicao'),
    path('deletar_instituicao/<int:id_inst>', deletar_instituicao, name='deletar_instituicao'),
    path('nova_instituicao/', nova_instituicao, name='nova_instituicao'),
    path('nova_atividade/', nova_atividade, name='nova_atividade'),
    path('editar_atividade/<int:id_atividade>', editar_atividade, name='editar_atividade'),
    path('deletar_atividade/<int:id_atividade>', deletar_atividade, name='deletar_atividade'),
    path('deletar_sequencia/<int:id_atividade>', deletar_sequencia, name='deletar_sequencia'),
    path('nova_atividade/get_valor_fixo/<int:instituicao_id>/', get_valor_fixo, name='get_valor_fixo'),
    path('atividade/<int:id_atividade>', atividade, name='atividade'),
    path('instituicao/<int:id_instituicao>', instituicao, name='instituicao'),
    path('financeiro/', financeiro, name='financeiro'),
    path('rotina/', rotina, name='rotina'),
    path('atualizar_financeiro/', atualizar_financeiro, name='atualizar_financeiro'),
    path('atualizar_grafico/', atualizar_grafico, name='atualizar_grafico'),
    path('atualizar_rotina/', atualizar_rotina, name='atualizar_rotina'),
    path('atualizar_grafico_rotina/', atualizar_grafico_rotina, name='atualizar_grafico_rotina')
]