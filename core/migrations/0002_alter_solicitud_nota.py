# Generated by Django 4.2.6 on 2023-11-18 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitud',
            name='nota',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
    ]
