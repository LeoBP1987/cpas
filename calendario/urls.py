from django.urls import path
from calendario.views import configuracoes

urlpatterns = [
    path('configuracoes/', configuracoes, name='configuracoes'),
]