# Generated by Django 5.1.1 on 2024-10-14 16:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('vehicle_type', '0002_auto_20241014_0215'),
    ]

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('region_id', models.AutoField(primary_key=True, serialize=False)),
                ('region_name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='PricingModel',
            fields=[
                ('pricing_id', models.AutoField(primary_key=True, serialize=False)),
                ('base_fare', models.DecimalField(decimal_places=2, max_digits=10)),
                ('per_km_rate', models.DecimalField(decimal_places=2, max_digits=10)),
                ('per_minute_rate', models.DecimalField(decimal_places=2, max_digits=10)),
                ('surge_multiplier', models.DecimalField(decimal_places=2, default=1.0, max_digits=4)),
                ('effective_start_date', models.DateField()),
                ('effective_end_date', models.DateField(blank=True, null=True)),
                ('vehicle_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pricing_models', to='vehicle_type.vehicletype')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pricing_models', to='pricing_model.region')),
            ],
        ),
        migrations.CreateModel(
            name='SurgePricing',
            fields=[
                ('surge_pricing_id', models.AutoField(primary_key=True, serialize=False)),
                ('surge_multiplier', models.DecimalField(decimal_places=2, max_digits=4)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='surge_pricings', to='pricing_model.region')),
                ('vehicle_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='surge_pricings', to='vehicle_type.vehicletype')),
            ],
        ),
    ]
