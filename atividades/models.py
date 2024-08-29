from django.db import models

class Categoria(models.Model):
    nome_categoria = models.CharField(max_length=30)

    def __str__(self):
        return self.nome_categoria

class TipoAtividade(models.Model):
    nome_tipo = models.CharField(max_length=30, null=False, blank=False)
    categoria = models.ForeignKey(
        to=Categoria,
        on_delete=models.SET_NULL,
        null=True,
        related_name='categorias'
    )

    def __str__(self):
        return self.nome_tipo

class Instituicao(models.Model):
    nome_curto = models.CharField(max_length=25, null=True, blank=True)
    nome_inst = models.CharField(max_length=50, null=False, blank=False)
    imagem = models.ImageField(upload_to='instituicao/%Y/%m/%d', blank=True, null=True)
    fixo_mensal_inst = models.BooleanField(default=False, null=True, blank=True)
    cod_fixo = models.CharField(max_length=10, null=True, blank=True)
    valor_fixo = models.CharField(max_length=50, blank=True, null=True)
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
        ('3', 'Quinzenal'),
        ('4', 'Mensal'),
    ]

    SEQ_PERSO = [
        (0, '1ª'),
        (1, '2ª'),
        (2, '3ª'),
        (3, '4ª'),
        (4, '5ª')
    ]

    HORAS_ENT = [
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
        (23, '23:00')
    ]

    HORAS_SAI = [
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
        (24, '00:00')
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
    valor = models.CharField(max_length=50, null=True, blank=True)
    sequencia = models.CharField(max_length=1, choices=SEQUENCIA, null=True, blank=True)
    seq_personalizada = models.CharField(max_length=10, null=True, blank=True)
    data_final_seq = models.DateField(null=True, blank=True)
    obs = models.TextField(null=True, blank=True)
    cod = models.IntegerField(null=True, blank=True)
    id_vir = models.IntegerField(null=True, blank=True)
    nao_remunerado = models.BooleanField(default=False, null=True, blank=True)
    fixo_mensal_ativ = models.BooleanField(default=False, null=True, blank=True)
    cod_fixo_ativ = models.CharField(max_length=10, null=True, blank=True)
    
    def __str__(self):
        return str(self.id)
    
class Preferencias(models.Model):
    horas_sono = models.IntegerField()
    tipo_grafico = models.CharField(max_length=10)