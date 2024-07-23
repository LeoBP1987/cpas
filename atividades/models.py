from django.db import models

class TipoAtividade(models.Model):
    nome_tipo = models.CharField(max_length=30, null=False, blank=False)
    horas = models.IntegerField()

class Instituicao(models.Model):
    nome_inst = models.CharField(max_length=33, null=False, blank=False)
    imagem = models.ImageField(upload_to='instituicao/%Y/%m/%d', blank='True', null='True')
    valor_padrao = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    endereco = models.CharField(max_length=255,)
    telefone = models.CharField(max_length=15,)
    contato = models.CharField(max_length=35,)

class Atividades(models.Model):
    intituicao = models.ForeignKey(
        to=Instituicao,
        on_delete=models.SET_NULL,
        null=True,
        related_name='atividades'
    )
    tipo_atividade = models.ForeignKey(
        to=TipoAtividade,
        on_delete=models.SET_NULL,
        null=True,
        related_name='tipo'
    )
    data = models.DateTimeField()
    entrada = models.TimeField()
    saida = models.TimeField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    sequencia = models.IntegerField()
    data_final_seq = models.DateTimeField()