from django.db import migrations
from django.conf import settings
import json
import os

def load_initial_data(apps, schema_editor):
    Region = apps.get_model('pricing_model', 'Region')
    PricingModel = apps.get_model('pricing_model', 'PricingModel')
    SurgePricing = apps.get_model('pricing_model', 'SurgePricing')
    VehicleType = apps.get_model('vehicle_type', 'VehicleType')

    # Load Regions
    base_dir = settings.BASE_DIR
    data_path = os.path.join(base_dir, 'pricing_model', 'data')
    
    with open(os.path.join(data_path, 'regions.json')) as f:
        regions = json.load(f)
        for region_data in regions:
            Region.objects.create(**region_data)

    # Load Base Pricing Models
    with open(os.path.join(data_path, 'pricing_models.json')) as f:
        pricing_models = json.load(f)
        
        for pm_data in pricing_models:
            vehicle_type_name = pm_data.pop('vehicle_type_name')
            region_name = pm_data.pop('region_name')
            try:
                vehicle_type = VehicleType.objects.get(type_name=vehicle_type_name)
                region = Region.objects.get(region_name=region_name)
                PricingModel.objects.create(vehicle_type=vehicle_type, region=region, **pm_data)
                
            except VehicleType.DoesNotExist:
                print(f"VehicleType '{vehicle_type_name}' does not exist for Base Pricing.")
            except Region.DoesNotExist:
                print(f"Region '{region_name}' does not exist for Base Pricing.")

    # Load Surge Pricings
    with open(os.path.join(data_path, 'surge_pricings.json')) as f:
        surge_pricings = json.load(f)
        for sp_data in surge_pricings:
            vehicle_type_name = sp_data.pop('vehicle_type_name')
            region_name = sp_data.pop('region_name')
            
            try:
                vehicle_type = VehicleType.objects.get(type_name=vehicle_type_name)
                region = Region.objects.get(region_name=region_name)
                SurgePricing.objects.create(vehicle_type=vehicle_type, region=region, **sp_data)
                
            except VehicleType.DoesNotExist:
                print(f"VehicleType '{vehicle_type_name}' does not exist for Surge Pricing.")
            except Region.DoesNotExist:
                print(f"Region '{region_name}' does not exist for Surge Pricing.")

class Migration(migrations.Migration):

    dependencies = [
        ('pricing_model', '0001_initial'),
        ('vehicle_type', '0002_auto_20241014_0215'),
    ]

    operations = [
        migrations.RunPython(load_initial_data),
    ]