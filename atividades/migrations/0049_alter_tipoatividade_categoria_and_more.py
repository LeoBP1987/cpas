# Generated by Django 5.0.7 on 2024-08-26 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atividades', '0048_alter_tipoatividade_nome_tipo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tipoatividade',
            name='categoria',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='tipoatividade',
            name='nome_tipo',
            field=models.CharField(max_length=30),
        ),
    ]
