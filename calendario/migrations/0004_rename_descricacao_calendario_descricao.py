# Generated by Django 5.0.7 on 2024-07-22 23:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calendario', '0003_rename_horas_calendario'),
    ]

    operations = [
        migrations.RenameField(
            model_name='calendario',
            old_name='descricacao',
            new_name='descricao',
        ),
    ]