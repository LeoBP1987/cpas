# Generated by Django 5.0.7 on 2024-08-21 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atividades', '0043_atividades_seq_pesonalizada'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atividades',
            name='seq_pesonalizada',
            field=models.CharField(blank=True, choices=[(0, '1ª'), (1, '2ª'), (2, '3ª'), (3, '4ª'), (4, '5ª')], max_length=10, null=True),
        ),
    ]