# Generated by Django 5.0.7 on 2024-07-24 23:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atividades', '0017_alter_atividades_data_final_seq_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atividades',
            name='valor',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]