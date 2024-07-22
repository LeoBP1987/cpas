from django.db import models

class Calendario(models.Model):
    dia = models.CharField(max_length=8)
    range = models.IntegerField()
    ocupado = models.BooleanField()
    descricao = models.TextField()