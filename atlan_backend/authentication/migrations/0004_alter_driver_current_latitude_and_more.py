# Generated by Django 5.1.1 on 2024-10-16 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_driver_current_latitude_driver_current_longitude'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driver',
            name='current_latitude',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='driver',
            name='current_longitude',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=9, null=True),
        ),
    ]