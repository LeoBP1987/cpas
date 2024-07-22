from django.urls import path
from calendario.views import configuracoes, gerar_calendario, apagar

urlpatterns = [
    path('configuracoes/', configuracoes, name='configuracoes'),
    path('gerar_calendario', gerar_calendario, name='gerar_calendario'),
    path('apagar/', apagar, name='apagar'),
]