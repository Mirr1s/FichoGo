# Generated by Django 5.2.1 on 2025-05-24 03:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_ficho_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='ficho',
            name='hora_validacion',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
