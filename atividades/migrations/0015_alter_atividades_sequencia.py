# Generated by Django 5.0.7 on 2024-07-23 23:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atividades', '0014_alter_atividades_data_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atividades',
            name='sequencia',
            field=models.CharField(choices=[('1', 'dia'), ('2', 'semana'), ('3', 'mes')], max_length=1, null=True),
        ),
    ]