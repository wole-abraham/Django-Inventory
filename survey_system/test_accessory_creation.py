#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'survey_system.settings')
django.setup()

from inventory.models import Accessory

# Test creating an accessory
try:
    accessory = Accessory.objects.create(
        name="Test Tripod",
        manufacturer="Test Manufacturer", 
        condition="Good",
        status="Good",
        return_status="In Store"
    )
    print(f"Successfully created accessory: {accessory.name}")
    print(f"Total accessories in database: {Accessory.objects.count()}")
except Exception as e:
    print(f"Error creating accessory: {e}")
    print("This might be a database migration issue.")
