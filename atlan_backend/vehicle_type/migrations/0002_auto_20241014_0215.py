# vehicle_type/migrations/0002_auto.py
from django.db import migrations

def populate_vehicle_types(apps, schema_editor):
    VehicleType = apps.get_model('vehicle_type', 'VehicleType')
    
    # Data to be inserted
    vehicle_types = [
        {"type_name": "2 wheeler", "description": "40cm x 40 cm x 40 cm", "base_price_per_km": 5, "capacity": 20, "image_url": None},
        {"type_name": "3 wheeler", "description": "5.5 ft x 4.5 ft x 5 ft", "base_price_per_km": 12, "capacity": 500, "image_url": None},
        {"type_name": "pickup 9ft", "description": "9ft x 5.5ft x 5.5 ft", "base_price_per_km": 20, "capacity": 1700, "image_url": None},
        {"type_name": "14ft", "description": "14ft x 6 ft x 6 ft", "base_price_per_km": 40, "capacity": 3500, "image_url": None},
    ]
    
    # Insert data into the table
    for vehicle in vehicle_types:
        VehicleType.objects.create(**vehicle)

class Migration(migrations.Migration):

    dependencies = [
        ('vehicle_type', '0001_initial'),  # This is your initial migration dependency
    ]

    operations = [
        migrations.RunPython(populate_vehicle_types),
    ]