# Generated by Django 5.0.7 on 2024-08-22 04:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atividades', '0045_alter_atividades_seq_pesonalizada'),
    ]

    operations = [
        migrations.RenameField(
            model_name='atividades',
            old_name='seq_pesonalizada',
            new_name='seq_personalizada',
        ),
    ]
