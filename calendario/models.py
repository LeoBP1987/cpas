from django.db import models

class Horas(models.Model):
    dia = models.CharField(max_length=8)
    range = models.IntegerField()
    ocupado = models.BooleanField()
    descricacao = models.TextField()

class Dia(models.Model):
    horas = models.ManyToManyField(
        to=Horas,
        related_name='dias'        
    )

class Mes(models.Model):
    dias = models.ManyToManyField(
        to=Dia,
        related_name='meses'
    )

class Ano(models.Model):
    meses = models.ManyToManyField(
        to=Mes,
        related_name='anos'
    )

class Calendario(models.Model):
    anos = models.ManyToManyField(
        to=Ano,
        related_name='calendarios'
    )
