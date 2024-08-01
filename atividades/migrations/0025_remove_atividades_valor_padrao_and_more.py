# Generated by Django 5.0.7 on 2024-07-25 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atividades', '0024_alter_atividades_sequencia'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='atividades',
            name='valor_padrao',
        ),
        migrations.AlterField(
            model_name='atividades',
            name='sequencia',
            field=models.CharField(blank=True, choices=[('', 'Sem Repetição'), (1, 'Dias Úteis'), (2, 'Semanal'), (3, 'Mensal')], max_length=1, null=True),
        ),
    ]