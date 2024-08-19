from django.urls import path
from calendario.views import configuracoes, gerar_calendario, apagar, disponibilidade, disponibilidade_saida, \
                            validar_sequencia, exibir_calendario, atualizar_calendario, atualizar_calendario_semana


urlpatterns = [
    path('configuracoes/', configuracoes, name='configuracoes'),
    path('gerar_calendario', gerar_calendario, name='gerar_calendario'),
    path('apagar/', apagar, name='apagar'),
    path('disponibilidade/', disponibilidade, name='disponibilidade'),
    path('disponibilidade_saida/', disponibilidade_saida, name='disponibilidade_saida'),
    path('validar_sequencia/', validar_sequencia, name='validar_sequencia'),
    path('exibir_calendario/', exibir_calendario, name='calendario'),
    path('atualizar_calendario/', atualizar_calendario, name='atualizar_calendario'),
    path('atualizar_calendario_semana/', atualizar_calendario_semana, name='atualizar_calendario_semana')
]