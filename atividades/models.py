from django.db import models

class TipoAtividade(models.Model):
    nome_tipo = models.CharField(max_length=30, null=False, blank=False)
    horas = models.IntegerField()

    def __str__(self):
        return self.nome_tipo

class Instituicao(models.Model):
    nome_inst = models.CharField(max_length=33, null=False, blank=False)
    imagem = models.ImageField(upload_to='instituicao/%Y/%m/%d', blank='True', null='True')
    valor_padrao = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    endereco = models.CharField(max_length=255,)
    telefone = models.CharField(max_length=15,)
    contato = models.CharField(max_length=35,)

    def __str__(self):
        return self.nome_inst

class Atividades(models.Model):

    SEQUENCIA = [
        ('', 'Sem Repetição'),
        ('1', 'Dias Úteis'),
        ('2', 'Semanal'),
        ('3', 'Mensal')
    ]

    HORAS = [
        (0, '00:00'),
        (1, '01:00'),
        (2, '02:00'),
        (3, '03:00'),
        (4, '04:00'),
        (5, '05:00'),
        (6, '06:00'),
        (7, '07:00'),
        (8, '08:00'),
        (9, '09:00'),
        (10, '10:00'),
        (11, '11:00'),
        (12, '12:00'),
        (13, '13:00'),
        (14, '14:00'),
        (15, '15:00'),
        (16, '16:00'),
        (17, '17:00'),
        (18, '18:00'),
        (19, '19:00'),
        (20, '20:00'),
        (21, '21:00'),
        (22, '22:00'),
        (23, '23:00'),
    ]

    instituicao = models.ForeignKey(
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
    data = models.DateField()
    entrada = models.IntegerField()
    saida = models.IntegerField()
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sequencia = models.CharField(max_length=1, choices=SEQUENCIA, null=True, blank=True)
    data_final_seq = models.DateField(null=True, blank=True)
    obs = models.TextField(null=True, blank=True)
    cod = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.tipo_atividade} no {self.instituicao}, {self.data} das {self.entrada} às {self.saida}'