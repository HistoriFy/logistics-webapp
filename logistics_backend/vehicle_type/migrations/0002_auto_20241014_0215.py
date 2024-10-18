# vehicle_type/migrations/0002_auto.py
from django.db import migrations
from django.conf import settings
import json
import os

def populate_vehicle_types(apps, schema_editor):
    VehicleType = apps.get_model('vehicle_type', 'VehicleType')
    
    base_dir = settings.BASE_DIR
    data_path = os.path.join(base_dir, 'vehicle_type', 'data', 'vehicle_types.json')
    
    with open(data_path,'r') as file:
        vehicle_types = json.load(file)
    
    for vehicle in vehicle_types:
        VehicleType.objects.update_or_create(
            type_name=vehicle['type_name'],  
            defaults=vehicle
        )

class Migration(migrations.Migration):

    dependencies = [
        ('vehicle_type', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_vehicle_types),
    ]