# Generated by Django 5.0.7 on 2024-08-14 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atividades', '0036_atividades_nao_remunerado_alter_atividades_sequencia'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tipoatividade',
            name='horas',
        ),
        migrations.AddField(
            model_name='tipoatividade',
            name='categoria',
            field=models.CharField(default='Trabalho', max_length=30),
        ),
    ]
