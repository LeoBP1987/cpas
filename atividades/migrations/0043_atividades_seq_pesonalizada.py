# Generated by Django 5.0.7 on 2024-08-21 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atividades', '0042_atividades_cod_fixo_ativ_instituicao_cod_fixo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='atividades',
            name='seq_pesonalizada',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
