# Generated by Django 5.1.1 on 2024-10-16 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_driver_available_bookings_driver_rating_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='current_latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='driver',
            name='current_longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
    ]