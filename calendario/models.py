from django.db import models
from atividades.models import Atividades

class Calendario(models.Model):
    dia = models.CharField(max_length=8)
    range = models.IntegerField()
    ocupado = models.BooleanField(default=False)
    atividades = models.ManyToManyField(
        to=Atividades,
        related_name="calendarios"
    )