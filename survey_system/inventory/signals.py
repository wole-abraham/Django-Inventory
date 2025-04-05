from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import EquipmentsInSurvey
from .emails import return_equipment_email
import requests


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