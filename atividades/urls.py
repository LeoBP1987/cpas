from django.urls import path
from atividades.views import index, novo_tipo, nova_instituicao

urlpatterns = [
    path('', index, name='index'),
    path('novo_tipo/', novo_tipo, name='novo_tipo'),
    path('nova_instituicao/', nova_instituicao, name='nova_instituicao')
]