# Generated by Django 4.2.6 on 2023-11-01 01:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_solicitud_profesor_user_solicitudes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="rol",
            field=models.CharField(default="Alumno", max_length=15),
        ),
        migrations.AlterField(
            model_name="user",
            name="rut",
            field=models.CharField(max_length=12),
        ),
    ]
