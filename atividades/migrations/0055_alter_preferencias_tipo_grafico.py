# Generated by Django 5.0.7 on 2024-09-10 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atividades', '0054_alter_preferencias_inicio_semana'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preferencias',
            name='tipo_grafico',
            field=models.CharField(default='bar', max_length=10),
        ),
    ]