from django.core.management.base import BaseCommand
from inventory.models import Accessory, EquipmentsInSurvey
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Debug accessory-equipment relationships'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Accessory-Equipment Relationship Debug ==='))
        
        # Show all equipment with their accessories
        equipment_list = EquipmentsInSurvey.objects.all().order_by('id')
        
        for equipment in equipment_list:
            self.stdout.write(f'\nEquipment: {equipment.name} (ID: {equipment.id})')
            self.stdout.write(f'  Status: {equipment.status}')
            self.stdout.write(f'  Chief Surveyor: {equipment.chief_surveyor}')
            self.stdout.write(f'  Total Accessories: {equipment.accessories.count()}')
            
            accessories = equipment.accessories.all()
            if accessories:
                for accessory in accessories:
                    self.stdout.write(f'    - {accessory.name} (ID: {accessory.id})')
                    self.stdout.write(f'      Status: {accessory.status}')
                    self.stdout.write(f'      Return Status: {accessory.return_status}')
                    self.stdout.write(f'      Chief Surveyor: {accessory.chief_surveyor}')
                    self.stdout.write(f'      Equipment Link: {accessory.equipment.name if accessory.equipment else "None"}')
            else:
                self.stdout.write('    No accessories linked')
        
        # Show accessories without equipment links
        self.stdout.write(f'\n=== Accessories Without Equipment Links ===')
        orphaned_accessories = Accessory.objects.filter(equipment__isnull=True)
        self.stdout.write(f'Found {orphaned_accessories.count()} accessories without equipment links')
        
        for accessory in orphaned_accessories[:10]:  # Show first 10
            self.stdout.write(f'  - {accessory.name} (ID: {accessory.id}) - Status: {accessory.return_status}')
        
        # Show accessories with different statuses
        self.stdout.write(f'\n=== Accessories by Status ===')
        statuses = ['In Store', 'Delivering', 'With Chief Surveyor', 'In Use', 'Returning', 'Returned']
        for status in statuses:
            count = Accessory.objects.filter(return_status=status).count()
            self.stdout.write(f'  {status}: {count} accessories')
