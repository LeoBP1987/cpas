# Generated by Django 5.0.7 on 2024-09-10 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atividades', '0053_preferencias_inicio_semana'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preferencias',
            name='inicio_semana',
            field=models.CharField(choices=[(0, 'Segunda-Feira'), (1, 'Domingo'), (2, 'Sábado'), (3, 'Sexta-Feira'), (4, 'Quinta-Feira'), (5, 'Quarta-Feira'), (6, 'Terça-Feira')], default=1, max_length=15),
        ),
    ]
