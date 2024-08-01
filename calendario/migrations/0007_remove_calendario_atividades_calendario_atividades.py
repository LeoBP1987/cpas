# Generated by Django 5.0.7 on 2024-07-23 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atividades', '0012_atividades'),
        ('calendario', '0006_remove_calendario_atividades_calendario_atividades'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='calendario',
            name='atividades',
        ),
        migrations.AddField(
            model_name='calendario',
            name='atividades',
            field=models.ManyToManyField(related_name='calendarios', to='atividades.atividades'),
        ),
    ]
