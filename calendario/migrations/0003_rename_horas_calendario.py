# Generated by Django 5.0.7 on 2024-07-22 22:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calendario', '0002_remove_calendario_anos_remove_dia_horas_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Horas',
            new_name='Calendario',
        ),
    ]
