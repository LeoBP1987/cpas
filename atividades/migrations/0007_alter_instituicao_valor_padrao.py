# Generated by Django 5.0.7 on 2024-07-23 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atividades', '0006_alter_instituicao_imagem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instituicao',
            name='valor_padrao',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
