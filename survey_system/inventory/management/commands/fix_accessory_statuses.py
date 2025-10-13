from django.core.management.base import BaseCommand
from inventory.models import Accessory, EquipmentsInSurvey

class Command(BaseCommand):
    help = 'Fix accessory statuses to match their equipment status'

    def handle(self, *args, **options):
        # Fix accessories that are linked to equipment but have wrong status
        accessories_with_equipment = Accessory.objects.filter(
            equipment__isnull=False,
            chief_surveyor__isnull=False
        )
        
        fixed_count = 0
        
        for accessory in accessories_with_equipment:
            equipment = accessory.equipment
            
            # Update accessory status based on equipment status
            if equipment.status == 'Delivering' and accessory.return_status != 'Delivering':
                accessory.return_status = 'Delivering'
                accessory.save()
                fixed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Fixed accessory "{accessory.name}" status to Delivering for equipment "{equipment.name}"')
                )
            elif equipment.status == 'With Chief Surveyor' and accessory.return_status not in ['With Chief Surveyor', 'In Use']:
                accessory.return_status = 'With Chief Surveyor'
                accessory.save()
                fixed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Fixed accessory "{accessory.name}" status to With Chief Surveyor for equipment "{equipment.name}"')
                )
            elif equipment.status == 'In Field' and accessory.return_status != 'In Use':
                accessory.return_status = 'In Use'
                accessory.save()
                fixed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Fixed accessory "{accessory.name}" status to In Use for equipment "{equipment.name}"')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Fixed {fixed_count} accessory statuses')
        )
