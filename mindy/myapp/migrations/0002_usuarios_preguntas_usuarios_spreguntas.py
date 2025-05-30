# Generated by Django 5.2 on 2025-05-13 20:02

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuarios',
            name='preguntas',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='usuarios',
            name='spreguntas',
            field=models.CharField(choices=[('0', '¿Cuál fue su primer colegio?'), ('1', '¿Nombre de su primera mascota?'), ('2', '¿Nombre de su pariente más cercano?'), ('3', '¿Año de expedición de la cedula?'), ('4', '¿Cuál es su flor favorita?')], default=django.utils.timezone.now, max_length=20),
            preserve_default=False,
        ),
    ]
