# Generated by Django 5.0.7 on 2024-07-23 21:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atividades', '0010_rename_intituicao_atividades_instituicao'),
        ('calendario', '0006_remove_calendario_atividades_calendario_atividades'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Atividades',
        ),
    ]
