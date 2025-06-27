from hashlib import blake2b
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.

# class Equipment(models.Model):
#     EQUIPMENT_TYPES =[
#         ('GNSS', 'GNSS'),
#         ('Total Station', 'Total Station'),
#         ('Level Instrumet', 'Level Instrument'),
#         ('Drone', 'Drone'),
#     ]

#     STATUS = [
#         ('In Field', 'In Field'),
#         ('Returning', 'Returning'),
#         ('In Store', 'In Store')
#     ]
#     name = models.CharField(max_length=100)
#     equipment_type = models.CharField(max_length=50, choices=EQUIPMENT_TYPES)
    
#     status = models.CharField(max_length=20, default='In Store', choices=STATUS)
#     requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
#     image = models.ImageField(upload_to='equipment_images/', null=True)
#     serial_number_roover = models.CharField(max_length=100, null=True)
#     base_serial = models.CharField(max_length=100, null=True)
#     supplier_name = models.CharField(max_length=100, null=True)





    # def __str__(self):
    #     return f"{self.name} ({self.equipment_type}) - {self.status}"





class EquipmentsInSurvey(models.Model):

    EQUIPMENT_CHOICES = [
        ('GNSS base-roover', 'GNSS base-roover'),
        ('GNSS roover', 'GNSS roover'),
        ('GNSS base', 'GNSS base'),
        ('Total Station', "Total Station"),
        ('Level Instruments', "Level Instrument"),
        ('Drone', 'Drone'),
        ('Eco Sounder', 'Eco Sounder'),
        ('Machine Control', 'Machine Control'),
        ('3d Scanner', '3d Scanner')
    ]

    supplier_name = [
        ('Hi Target', 'Hi Targer'),
        ('TopCon', 'TopCon'),
        ('Leica', 'Leica'),
        ('Sokkia', 'Sokkia')
    ]
    
    owner_choice = [
        ('Company', "Company"),
        ("Sub-Contractor", "Sub-Contractor")
    ]

    name = models.CharField(max_length=100, help_text="Equipment Name", choices=EQUIPMENT_CHOICES)
    date_of_receiving_from_supplier = models.DateField(blank=True, null=True)
    supplier = models.CharField(max_length=20, choices=supplier_name)
    owner = models.CharField(max_length=20, choices=owner_choice)
    base_serial = models.CharField(max_length=100, null=True, blank=True)
    roover_serial = models.CharField(max_length=100, null=True, blank=True, help_text="Roover Serial Number")
    condition = models.CharField(max_length=20, choices=[("New", "New"), ("Second Hand", "Second Hand")], default="New")
    chief_surveyor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    surveyor_responsible = models.CharField(max_length=100, null=True, blank=True, help_text="Name of the surveyor responsible for the equipment")
    quantity = models.PositiveBigIntegerField(default=1, help_text="Number of Quantity")
    project = models.CharField(max_length=20, choices=[('Coastal Road', 'Coastal Road'), ('Sokoto', 'Sokoto')], blank=True, null=True, help_text="Project Name")
    section = models.CharField(max_length=100, null=True, blank=True)
    date_receiving_from_department = models.DateField(blank=True, null=True, help_text="Date when the equipment was received from the department")
    status = models.CharField(choices=[('In Store', 'In Store'), ('In Field', 'In Field'), ('With Chief Surveyor', 'With Chief Surveyor'), ('Returning', 'Returning'), ('Delivering', 'Delivering')], max_length=100, default='In Store', blank=True, null=True, help_text="Current status of the equipment")
    delivery_status = models.CharField(max_length=10, choices=[('Delivered', 'Delivered'), ('Delivering', 'Delivering'), ('Cancelled', 'Cancelled')], null=True, blank=True)

    def __str__(self):
        return f'{self.base_serial}'
    def __repr__(self):
        return f'{self.base_serial}'
 
# class SurveyorEngineer(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     requested_equipment = models.ManyToManyField(Equipment, blank=True)

#     def __str__(self):
#         return self.user.username
    
class Accessory(models.Model):
    ACCESSORY_TYPES = (
        ("tripod", "Tripod"),
        ("levelling_staff", "Levelling Staff"),
        ("GNSS Battery", "GNSS Battery"),
        ("Pole", "Pole"),
        ("Mini Prism", "Mini Prism"),
        ("Sheet", "Sheet"),
        ("Total Station prism", "Total Station Prism"),
        ("Radio", "Radio"),
        ("tracking_rod", "Tracking Rod"),
        ("reflector", "Reflector"),
        ("gps_extension_bar", "GPS Extension Bar"),
        ("bar_port", "Bar Port"),
        ("powerbank", "Powerbank"),
        ("tribach", "Tribach"),
        ("external_radio_antenna", "External Radio Antenna"),
        ("Data Lpgger", "Data Logger"),
        ("Radio Serial", "Radio Serial"),
    )

    STATUS_CHOICES = [
        ('Good', 'Good'),
        ('Needs Repair', 'Needs Repair'),
        ('Bad', 'Bad'),
    ]

    RETURN_STATUS_CHOICES = [
        ('In Use', 'In Use'),
        ('Returning', 'Returning'),
        ('Delivering', 'Delivering'),
        ('With Chief Surveyor', 'With Chief Surveyor'),
        ('In Store', 'In Store'),
        ('Returned', 'Returned'),
    ]

    name = models.CharField(max_length=100, choices=ACCESSORY_TYPES)
    serial_number = models.CharField(max_length=50, null=True, blank=True, help_text="Unique serial number for the accessory")
    equipment = models.ForeignKey(EquipmentsInSurvey, on_delete=models.CASCADE, related_name='accessories', null=True, blank=True)
    chief_surveyor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    surveyor_responsible = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Good', null=True, blank=True)
    return_status = models.CharField(max_length=20, choices=RETURN_STATUS_CHOICES, default='Returned', null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='accessory_images/', null=True, blank=True)
    date_returned = models.DateTimeField(null=True, blank=True)
    returned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='returned_accessories')
    delivery_status = models.CharField(max_length=10, choices=[('Delivered', 'Delivered'), ('Delivering', 'Delivering'), ('Cancelled', 'Cancelled')], null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    def mark_as_returned(self, user):
        self.return_status = 'Returning'
        self.date_returned = timezone.now()
        self.returned_by = user
        self.save()

class EquipmentHistory(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('released', 'Released'),
        ('returned', 'Returned'),
        ('status_changed', 'Status Changed'),
    ]

    equipment = models.ForeignKey(EquipmentsInSurvey, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    previous_status = models.CharField(max_length=20, null=True, blank=True)
    new_status = models.CharField(max_length=20, null=True, blank=True)
    previous_chief_surveyor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='previous_equipment_history')
    new_chief_surveyor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='new_equipment_history')
    comment = models.TextField(null=True, blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='equipment_changes')
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.equipment.name} - {self.action} by {self.changed_by} at {self.changed_at}"

class AccessoryHistory(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('released', 'Released'),
        ('returned', 'Returned'),
        ('status_changed', 'Status Changed'),
        ('image_uploaded', 'Image Uploaded'),
    ]

    accessory = models.ForeignKey(Accessory, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    previous_status = models.CharField(max_length=20, null=True, blank=True)
    new_status = models.CharField(max_length=20, null=True, blank=True)
    previous_return_status = models.CharField(max_length=20, null=True, blank=True)
    new_return_status = models.CharField(max_length=20, null=True, blank=True)
    previous_chief_surveyor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='previous_accessory_history')
    new_chief_surveyor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='new_accessory_history')
    comment = models.TextField(null=True, blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='accessory_changes')
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.accessory.name} - {self.action} by {self.changed_by} at {self.changed_at}"