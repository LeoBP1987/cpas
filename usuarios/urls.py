from django.urls import path
from usuarios.views import login, logout, alterar_senha

urlpatterns = [
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('alterar_senha/', alterar_senha, name='alterar_senha')
]