# Generated by Django 5.0.7 on 2024-08-13 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atividades', '0035_alter_instituicao_imagem'),
    ]

    operations = [
        migrations.AddField(
            model_name='atividades',
            name='nao_remunerado',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='atividades',
            name='sequencia',
            field=models.CharField(blank=True, choices=[('', 'Sem Repetição'), ('1', 'Dias Úteis'), ('2', 'Semanal'), ('3', 'Quinzenal'), ('4', 'Mensal')], max_length=1, null=True),
        ),
    ]
