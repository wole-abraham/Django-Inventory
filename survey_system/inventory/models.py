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
    serial_number_roover = models.CharField(max_length=100, null=True)
    base_serial = models.CharField(max_length=100, null=True)
    supplier_name = models.CharField(max_length=100, null=True)





    def __str__(self):
        return f"{self.name} ({self.equipment_type}) - {self.status}"

class SurveyorEngineer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    requested_equipment = models.ManyToManyField(Equipment, blank=True)

    def __str__(self):
        return self.user.username



class EquipmentsInSurvey(models.Model):
    name = models.CharField(max_length=100)
    date_of_receiving_from_supplier = models.DateField()
    supplier = models.CharField(max_length=20)
    base_serial = models.CharField(max_length=100)
    roover_serial = models.CharField(max_length=100)
    data_logger_serial = models.CharField(max_length=100)
    radio_serial = models.CharField(max_length=100)
    chief_surveyor = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    surveyor_responsible = models.CharField(max_length=100, null=True)
    project = models.CharField(max_length=20)
    section = models.CharField(max_length=100)
    date_receiving_from_department = models.DateField()
    status = models.CharField(choices=[('In Store', 'In Store'), ('In Field', 'In Field'), ('With Chief Surveyor', 'With Chief Surveyor')], max_length=100, default='In Store')

    def __str__(self):
        return f'{self.base_serial}'
    def __repr__(self):
        return f'{self.base_serial}'
 

    



