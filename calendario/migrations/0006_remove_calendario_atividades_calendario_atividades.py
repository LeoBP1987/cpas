# Generated by Django 5.0.7 on 2024-07-23 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendario', '0005_remove_calendario_descricao_calendario_atividades'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='calendario',
            name='atividades',
        ),
        migrations.AddField(
            model_name='calendario',
            name='atividades',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
