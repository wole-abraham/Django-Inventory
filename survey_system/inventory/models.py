from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Equipment(models.Model):
    EQUIPMENT_TYPES =[
        ('GNSS', 'GNSS'),
        ('Total Station', 'Total Station'),
        ('Level Instrumet', 'Level Instrument'),
        ('Drone', 'Drone'),
    ]

    STATUS = [
        ('In Field', 'In Field'),
        ('In Store', 'In Store')
    ]
    name = models.CharField(max_length=100)
    equipment_type = models.CharField(max_length=50, choices=EQUIPMENT_TYPES)
    status = models.CharField(max_length=20, default='In Store', choices=STATUS)
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='equipment_images/', null=True)


    def __str__(self):
        return f"{self.name} ({self.equipment_type}) - {self.status}"

class SurveyorEngineer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    requested_equipment = models.ManyToManyField(Equipment, blank=True)

    def __str__(self):
        return self.user.username