from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import EquipmentsInSurvey, Accessory, EquipmentHistory, AccessoryHistory
from .emails import return_equipment_email
import requests
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=EquipmentsInSurvey)
def notify_surveyor(sender, instance, created, **kwargs):
    if not created:
        if instance.status == 'Returning':
            equipment = instance
            # Use select_related to ensure the chief_surveyor is loaded with the equipment
            equipment = EquipmentsInSurvey.objects.select_related('chief_surveyor').get(id=equipment.id)
            message = return_equipment_email(equipment)
            requests.post(
                url ='https://hook.eu2.make.com/svxxuei9ivon08wka4dwjih5l2tfrkcy'
                , data= {"message": message}
            )

@receiver(post_save, sender=EquipmentsInSurvey)
def create_equipment_history(sender, instance, created, **kwargs):
    logger.info(f"Equipment history signal triggered for {instance.name} (created: {created})")
    if created:
        history = EquipmentHistory.objects.create(
            equipment=instance,
            action='created',
            new_status=instance.status,
            new_chief_surveyor=instance.chief_surveyor,
            changed_by=instance.chief_surveyor
        )
        logger.info(f"Created equipment history entry: {history}")
    else:
        # Get the previous state
        try:
            previous = EquipmentsInSurvey.objects.get(id=instance.id)
            if previous.status != instance.status or previous.chief_surveyor != instance.chief_surveyor:
                history = EquipmentHistory.objects.create(
                    equipment=instance,
                    action='updated',
                    previous_status=previous.status,
                    new_status=instance.status,
                    previous_chief_surveyor=previous.chief_surveyor,
                    new_chief_surveyor=instance.chief_surveyor,
                    changed_by=instance.chief_surveyor
                )
                logger.info(f"Created equipment history update entry: {history}")
        except EquipmentsInSurvey.DoesNotExist:
            logger.warning(f"Previous equipment state not found for {instance.id}")

@receiver(post_save, sender=Accessory)
def create_accessory_history(sender, instance, created, **kwargs):
    logger.info(f"Accessory history signal triggered for {instance.name} (created: {created})")
    if created:
        history = AccessoryHistory.objects.create(
            accessory=instance,
            action='created',
            new_status=instance.status,
            new_return_status=instance.return_status,
            new_chief_surveyor=instance.chief_surveyor,
            changed_by=instance.chief_surveyor
        )
        logger.info(f"Created accessory history entry: {history}")
    else:
        # Get the previous state
        try:
            previous = Accessory.objects.get(id=instance.id)
            if (previous.status != instance.status or 
                previous.return_status != instance.return_status or 
                previous.chief_surveyor != instance.chief_surveyor):
                history = AccessoryHistory.objects.create(
                    accessory=instance,
                    action='updated',
                    previous_status=previous.status,
                    new_status=instance.status,
                    previous_return_status=previous.return_status,
                    new_return_status=instance.return_status,
                    previous_chief_surveyor=previous.chief_surveyor,
                    new_chief_surveyor=instance.chief_surveyor,
                    changed_by=instance.chief_surveyor
                )
                logger.info(f"Created accessory history update entry: {history}")
        except Accessory.DoesNotExist:
            logger.warning(f"Previous accessory state not found for {instance.id}")