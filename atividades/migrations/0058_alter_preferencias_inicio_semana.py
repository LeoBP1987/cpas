# Generated by Django 5.0.7 on 2024-09-10 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atividades', '0057_alter_preferencias_hora_envio_tarefas_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preferencias',
            name='inicio_semana',
            field=models.CharField(default=1, max_length=15),
        ),
    ]