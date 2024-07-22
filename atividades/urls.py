from django.urls import path
from atividades.views import index

urlpatterns = [
    path('', index, name='index'),
]