from django.core.management.base import BaseCommand
from inventory.models import Accessory, EquipmentsInSurvey

class Command(BaseCommand):
    help = 'Fix accessories that are not properly linked to equipment'

    def handle(self, *args, **options):
        # Find accessories that have the same chief_surveyor as equipment but no equipment link
        accessories_without_equipment = Accessory.objects.filter(
            equipment__isnull=True,
            chief_surveyor__isnull=False
        )
        
        fixed_count = 0
        
        for accessory in accessories_without_equipment:
            # Try to find equipment with the same chief_surveyor and similar status
            if accessory.return_status == 'Delivering':
                equipment = EquipmentsInSurvey.objects.filter(
                    chief_surveyor=accessory.chief_surveyor,
                    status='Delivering'
                ).first()
            elif accessory.return_status == 'With Chief Surveyor':
                equipment = EquipmentsInSurvey.objects.filter(
                    chief_surveyor=accessory.chief_surveyor,
                    status='With Chief Surveyor'
                ).first()
            else:
                equipment = EquipmentsInSurvey.objects.filter(
                    chief_surveyor=accessory.chief_surveyor
                ).first()
            
            if equipment:
                accessory.equipment = equipment
                accessory.save()
                fixed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Linked accessory "{accessory.name}" to equipment "{equipment.name}"')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Fixed {fixed_count} accessory-equipment links')
        )
