# Generated by Django 5.2.1 on 2025-05-21 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0003_registrosensor"),
    ]

    operations = [
        migrations.AddField(
            model_name="datosensor",
            name="device",
            field=models.CharField(default=None, max_length=50),
        ),
        migrations.AddField(
            model_name="datosensor",
            name="userId",
            field=models.CharField(default=None, max_length=64),
        ),
    ]
