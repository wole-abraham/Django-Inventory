from hashlib import blake2b
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
import uuid

# Create your models here.

def generate_serial_number():
    """Generate a unique serial number for accessories"""
    return f"ACC-{uuid.uuid4().hex[:8].upper()}"

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
        ('GPS Receiver (Base)', 'GPS Receiver (Base)'),
        ('GPS Receiver (Rover)', 'GPS Receiver (Rover)'),
        ('Data logger', 'Data logger'),
        ('External Radio', "External Radio"),
        ('Total Station', "Total Station"),
        ('Levelling Instrument', 'Levelling Instrument'),
        ('Eco Sounder', 'Eco Sounder'),
    ]

    # Removed supplier_name choices to allow any manufacturer/model from CSV
    
    owner_choice = [
        ('Hi-Tech', "Hi-Tech"),
        ("Sub-Contractor", "Sub-Contractor")
    ]

    name = models.CharField(max_length=100, help_text="Equipment Name", choices=EQUIPMENT_CHOICES)
    date_of_receiving_from_supplier = models.DateField(default=timezone.now, help_text="Date when equipment was received from supplier") 
    supplier = models.CharField(max_length=100, help_text="Manufacturer/Model from CSV")
    owner = models.CharField(max_length=20, choices=owner_choice)
    serial_number = models.CharField(max_length=100, help_text="Equipment Serial Number")
    condition = models.CharField(max_length=50, help_text="Equipment condition from CSV", default="Good")
    
    # Choices for equipment condition after use (when returning)
    CONDITION_AFTER_USE_CHOICES = [
        ("Good", "Good"),
        ("Need Repair", "Need Repair")
    ]
    chief_surveyor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    surveyor_responsible = models.CharField(max_length=100, null=False, blank=True, help_text="Name of the surveyor responsible for the equipment",  default="gap")
    quantity = models.PositiveBigIntegerField(default=1, help_text="Number of Quantity")
    project = models.CharField(max_length=20, choices=[('Coastal Road', 'Coastal Road'), ('Sokoto', 'Sokoto'), ('gap', 'gap')], blank=True, null=True, help_text="Project Name", default="gap")
    section = models.CharField(max_length=100, null=True, blank=True)
    date_receiving_from_department = models.DateField(default=timezone.now, help_text="Date when the equipment was received from the department")
    status = models.CharField(choices=[('In Store', 'In Store'), ('In Field', 'In Field'), ('With Chief Surveyor', 'With Chief Surveyor'), ('Returning', 'Returning'), ('Delivering', 'Delivering')], max_length=100, default='In Store', blank=True, null=True, help_text="Current status of the equipment")
    delivery_status = models.CharField(max_length=10, choices=[('Delivered', 'Delivered'), ('Delivering', 'Delivering'), ('Cancelled', 'Cancelled')], null=True, blank=True)
    return_comment = models.TextField(null=True, blank=True, help_text="Comment when equipment is returned", default="gap")
    return_date = models.DateTimeField(null=True, blank=True, help_text="Date when equipment was returned")

    def __str__(self):
        return f'{self.serial_number}'
    
    def __repr__(self):
        return f'{self.serial_number}'
    
    def log_history(self, action, changed_by=None, comment=None, **kwargs):
        """
        Helper method to log equipment history
        Usage: equipment.log_history('released', changed_by=request.user, comment='Released to field')
        """
        from .models import EquipmentHistory
        return EquipmentHistory.objects.create(
            equipment=self,
            action=action,
            changed_by=changed_by,
            comment=comment,
            **kwargs
        )
    
    def get_return_count(self):
        """Get the number of times this equipment has been returned to store"""
        return self.history.filter(
            action='returned',
            new_status='In Store'
        ).count()
    
    def get_release_count(self):
        """Get the number of times this equipment has been released"""
        return self.history.filter(
            action__in=['released', 'released_to_field']
        ).count()
    
    def get_history_summary(self):
        """Get a summary of equipment history"""
        return {
            'total_entries': self.history.count(),
            'returns_to_store': self.get_return_count(),
            'releases': self.get_release_count(),
            'last_action': self.history.first(),
            'created_date': self.history.filter(action='created').first(),
        }


class Personnel(models.Model):
    """Model for personnel (surveyors, engineers, etc.)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='personnel_profile')
    employee_id = models.CharField(max_length=20, unique=True, help_text="Employee ID")
    position = models.CharField(max_length=100, help_text="Job Position")
    department = models.CharField(max_length=100, help_text="Department")
    phone_number = models.CharField(max_length=15, blank=True, null=True, help_text="Phone Number")
    date_joined = models.DateField(auto_now_add=True, help_text="Date Joined")
    is_active = models.BooleanField(default=True, help_text="Active Status")
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"
    
    def get_assigned_chainmen(self):
        return self.chainmen.all()


class Chainman(models.Model):
    """Model for chainmen assigned to personnel"""
    name = models.CharField(max_length=100, help_text="Full Name")
    employee_id = models.CharField(max_length=20, unique=True, help_text="Employee ID")
    phone_number = models.CharField(max_length=15, blank=True, null=True, help_text="Phone Number")
    assigned_to = models.ForeignKey(Personnel, on_delete=models.SET_NULL, null=True, blank=True, related_name='chainmen', help_text="Assigned Personnel")
    date_assigned = models.DateField(auto_now_add=True, help_text="Date Assigned")
    is_active = models.BooleanField(default=True,  help_text="Active Status")
    
    def __str__(self):
        return f"{self.name} ({self.employee_id})"
 
# class SurveyorEngineer(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     requested_equipment = models.ManyToManyField(Equipment, blank=True)

#     def __str__(self):
#         return self.user.username
    
class Accessory(models.Model):
    ACCESSORY_TYPES = (
        # GPS AND ROVER ACCESSORIES
        ("tracking_rod", "Tracking Rod"),
        ("tripod", "Tripod"),
        ("external_radio", "External Radio"),
        ("car_battery", "Car battery"),
        ("base_pole", "Base pole"),
        ("tribrach", "Tribrach"),
        
        # TOTAL STATION ACCESSORIES
        ("reflector", "Reflector"),
        
        # LEVELLING INSTRUMENTS ACCESSORIES
        ("levelling_staff", "Levelling staff"),
        
        # ADDITIONAL ACCESSORIES
        ("GNSS Battery", "GNSS Battery"),
        ("Pole", "Pole"),
        ("Mini Prism", "Mini Prism"),
        ("Sheet", "Sheet"),
        ("Total Station prism", "Total Station Prism"),
        ("Radio", "Radio"),
        ("gps_extension_bar", "GPS Extension Bar"),
        ("bar_port", "Bar Port"),
        ("powerbank", "Powerbank"),
        ("external_radio_antenna", "External Radio Antenna"),
        ("Data Logger", "Data Logger"),
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

    name = models.CharField(max_length=100, help_text="Accessory name from CSV")
    manufacturer = models.CharField(max_length=100, null=True, blank=True, help_text="Manufacturer from CSV")
    serial_number = models.CharField(max_length=50, default=generate_serial_number, unique=True, help_text="Unique serial number for the accessory")
    equipment = models.ForeignKey(EquipmentsInSurvey, on_delete=models.CASCADE, related_name='accessories', null=True, blank=True)
    chief_surveyor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    surveyor_responsible = models.CharField(max_length=100, null=True, blank=True)
    condition = models.CharField(max_length=50, help_text="Physical condition from CSV", default='Good', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Good', null=True, blank=True)
    return_status = models.CharField(max_length=20, choices=RETURN_STATUS_CHOICES, default='In Store', null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    date_assigned = models.DateTimeField(null=True, blank=True, help_text="Date when accessory was assigned to user")
    date_returned = models.DateTimeField(null=True, blank=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_accessories')
    returned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='returned_accessories')
    delivery_status = models.CharField(max_length=10, choices=[('Delivered', 'Delivered'), ('Delivering', 'Delivering'), ('Cancelled', 'Cancelled'), ('gap', 'gap')], null=True, blank=True,default="gap")

    def __str__(self):
        return f"{self.name}"

    def mark_as_assigned(self, user, assigned_by=None, equipment_status=None, equipment=None):
        """Mark accessory as assigned to a user"""
        old_status = self.return_status
        old_chief = self.chief_surveyor
        old_equipment = self.equipment
        
        self.chief_surveyor = user
        self.date_assigned = timezone.now()
        if assigned_by:
            self.assigned_by = assigned_by
        
        # Link to equipment if provided
        if equipment:
            self.equipment = equipment
        
            # Set return_status based on equipment status
            if equipment_status == 'Delivering':
                self.return_status = 'Delivering'
            elif equipment_status == 'With Chief Surveyor':
                self.return_status = 'With Chief Surveyor'
            else:
                self.return_status = 'In Use'
            
            self.save()
        else:
            self.return_status = "Delivering"
            self.save()
        
        # Log history
        self.log_history(
            action='released',
            changed_by=assigned_by or user,
            previous_return_status=old_status,
            new_return_status=self.return_status,
            previous_chief_surveyor=old_chief,
            new_chief_surveyor=user,
            previous_equipment=str(old_equipment) if old_equipment else None,
            new_equipment=str(equipment) if equipment else None,
            comment=f"Assigned to {user.username}" + (f" with equipment {equipment}" if equipment else " as standalone")
        )

    def mark_as_returned(self, user):
        """Mark accessory as returned and deassign from equipment"""
        old_status = self.return_status
        
        self.return_status = 'Returning'  # Set to 'Returning' for admin approval
        self.date_returned = timezone.now()
        self.returned_by = user
        # Keep equipment link for tracking purposes, but mark as returning
        # Don't deassign from equipment until admin approves
        self.save()
        
        # Log history
        self.log_history(
            action='returned',
            changed_by=user,
            previous_return_status=old_status,
            new_return_status='Returning',
            comment=f"Returned by {user.username}"
        )
    
    def log_history(self, action, changed_by=None, comment=None, **kwargs):
        """
        Helper method to log accessory history
        Usage: accessory.log_history('released', changed_by=request.user, comment='Released to field')
        """
        from .models import AccessoryHistory
        return AccessoryHistory.objects.create(
            accessory=self,
            action=action,
            changed_by=changed_by,
            comment=comment,
            **kwargs
        )
    
    def get_return_count(self):
        """Get the number of times this accessory has been returned to store"""
        return self.history.filter(
            action='returned',
            new_return_status__in=['In Store', 'Returned']
        ).count()
    
    def get_release_count(self):
        """Get the number of times this accessory has been released"""
        return self.history.filter(
            action__in=['released', 'released_to_field']
        ).count()
    
    def get_history_summary(self):
        """Get a summary of accessory history"""
        return {
            'total_entries': self.history.count(),
            'returns_to_store': self.get_return_count(),
            'releases': self.get_release_count(),
            'last_action': self.history.first(),
            'created_date': self.history.filter(action='created').first(),
        }

class EquipmentHistory(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('released', 'Released to Chief Surveyor'),
        ('released_to_field', 'Released to Field'),
        ('returned', 'Returned to Store'),
        ('status_changed', 'Status Changed'),
        ('condition_changed', 'Condition Changed'),
        ('surveyor_changed', 'Surveyor Changed'),
        ('project_changed', 'Project Changed'),
        ('section_changed', 'Section Changed'),
        ('delivery_cancelled', 'Delivery Cancelled'),
        ('delivery_received', 'Delivery Received'),
    ]

    equipment = models.ForeignKey(EquipmentsInSurvey, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    
    # Status tracking
    previous_status = models.CharField(max_length=100, null=True, blank=True)
    new_status = models.CharField(max_length=100, null=True, blank=True)
    
    # Condition tracking
    previous_condition = models.CharField(max_length=50, null=True, blank=True)
    new_condition = models.CharField(max_length=50, null=True, blank=True)
    
    # User tracking
    previous_chief_surveyor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='previous_equipment_history')
    new_chief_surveyor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='new_equipment_history')
    
    # Surveyor responsible tracking
    previous_surveyor_responsible = models.CharField(max_length=100, null=True, blank=True)
    new_surveyor_responsible = models.CharField(max_length=100, null=True, blank=True)
    
    # Project and section tracking
    previous_project = models.CharField(max_length=20, null=True, blank=True)
    new_project = models.CharField(max_length=20, null=True, blank=True)
    previous_section = models.CharField(max_length=100, null=True, blank=True)
    new_section = models.CharField(max_length=100, null=True, blank=True)
    
    # Delivery tracking
    previous_delivery_status = models.CharField(max_length=10, null=True, blank=True)
    new_delivery_status = models.CharField(max_length=10, null=True, blank=True)
    
    comment = models.TextField(null=True, blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='equipment_changes')
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name = 'Equipment History'
        verbose_name_plural = 'Equipment Histories'

    def __str__(self):
        return f"{self.equipment.name} - {self.action} by {self.changed_by} at {self.changed_at}"
    
    def get_description(self):
        """Generate a human-readable description of the change"""
        descriptions = []
        
        if self.previous_status != self.new_status and self.new_status:
            descriptions.append(f"Status changed from '{self.previous_status or 'N/A'}' to '{self.new_status}'")
        
        if self.previous_condition != self.new_condition and self.new_condition:
            descriptions.append(f"Condition changed from '{self.previous_condition or 'N/A'}' to '{self.new_condition}'")
        
        if self.previous_chief_surveyor != self.new_chief_surveyor and self.new_chief_surveyor:
            prev_name = self.previous_chief_surveyor.username if self.previous_chief_surveyor else 'N/A'
            descriptions.append(f"Chief Surveyor changed from '{prev_name}' to '{self.new_chief_surveyor.username}'")
        
        if self.previous_surveyor_responsible != self.new_surveyor_responsible and self.new_surveyor_responsible:
            descriptions.append(f"Surveyor Responsible changed from '{self.previous_surveyor_responsible or 'N/A'}' to '{self.new_surveyor_responsible}'")
        
        if self.previous_project != self.new_project and self.new_project:
            descriptions.append(f"Project changed from '{self.previous_project or 'N/A'}' to '{self.new_project}'")
        
        if self.previous_section != self.new_section and self.new_section:
            descriptions.append(f"Section changed from '{self.previous_section or 'N/A'}' to '{self.new_section}'")
        
        if self.comment:
            descriptions.append(f"Comment: {self.comment}")
        
        return '; '.join(descriptions) if descriptions else self.action

class AccessoryHistory(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('released', 'Released to Chief Surveyor'),
        ('released_to_field', 'Released to Field'),
        ('returned', 'Returned to Store'),
        ('status_changed', 'Status Changed'),
        ('condition_changed', 'Condition Changed'),
        ('equipment_assigned', 'Assigned to Equipment'),
        ('equipment_removed', 'Removed from Equipment'),
        ('image_uploaded', 'Image Uploaded'),
        ('delivery_cancelled', 'Delivery Cancelled'),
        ('delivery_received', 'Delivery Received'),
    ]

    accessory = models.ForeignKey(Accessory, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    
    # Condition/Status tracking
    previous_status = models.CharField(max_length=20, null=True, blank=True)
    new_status = models.CharField(max_length=20, null=True, blank=True)
    previous_return_status = models.CharField(max_length=20, null=True, blank=True)
    new_return_status = models.CharField(max_length=20, null=True, blank=True)
    previous_condition = models.CharField(max_length=50, null=True, blank=True)
    new_condition = models.CharField(max_length=50, null=True, blank=True)
    
    # User tracking
    previous_chief_surveyor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='previous_accessory_history')
    new_chief_surveyor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='new_accessory_history')
    
    # Surveyor responsible tracking
    previous_surveyor_responsible = models.CharField(max_length=100, null=True, blank=True)
    new_surveyor_responsible = models.CharField(max_length=100, null=True, blank=True)
    
    # Equipment tracking
    previous_equipment = models.CharField(max_length=200, null=True, blank=True)
    new_equipment = models.CharField(max_length=200, null=True, blank=True)
    
    # Delivery tracking
    previous_delivery_status = models.CharField(max_length=20, null=True, blank=True)
    new_delivery_status = models.CharField(max_length=20, null=True, blank=True)
    
    comment = models.TextField(null=True, blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='accessory_changes')
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name = 'Accessory History'
        verbose_name_plural = 'Accessory Histories'

    def __str__(self):
        return f"{self.accessory.name} - {self.action} by {self.changed_by} at {self.changed_at}"
    
    def get_description(self):
        """Generate a human-readable description of the change"""
        descriptions = []
        
        if self.previous_status != self.new_status and self.new_status:
            descriptions.append(f"Status changed from '{self.previous_status or 'N/A'}' to '{self.new_status}'")
        
        if self.previous_return_status != self.new_return_status and self.new_return_status:
            descriptions.append(f"Return Status changed from '{self.previous_return_status or 'N/A'}' to '{self.new_return_status}'")
        
        if self.previous_condition != self.new_condition and self.new_condition:
            descriptions.append(f"Condition changed from '{self.previous_condition or 'N/A'}' to '{self.new_condition}'")
        
        if self.previous_chief_surveyor != self.new_chief_surveyor and self.new_chief_surveyor:
            prev_name = self.previous_chief_surveyor.username if self.previous_chief_surveyor else 'N/A'
            descriptions.append(f"Chief Surveyor changed from '{prev_name}' to '{self.new_chief_surveyor.username}'")
        
        if self.previous_surveyor_responsible != self.new_surveyor_responsible and self.new_surveyor_responsible:
            descriptions.append(f"Surveyor Responsible changed from '{self.previous_surveyor_responsible or 'N/A'}' to '{self.new_surveyor_responsible}'")
        
        if self.previous_equipment != self.new_equipment:
            if self.new_equipment:
                descriptions.append(f"Equipment changed from '{self.previous_equipment or 'None'}' to '{self.new_equipment}'")
            else:
                descriptions.append(f"Removed from equipment '{self.previous_equipment}'")
        
        if self.comment:
            descriptions.append(f"Comment: {self.comment}")
        
        return '; '.join(descriptions) if descriptions else self.action


@receiver(post_save, sender=Accessory)
def generate_accessory_serial_number(sender, instance, created, **kwargs):
    """Generate a unique serial number for accessories when they are created"""
    if created and not instance.serial_number:
        instance.serial_number = generate_serial_number()
        instance.save(update_fields=['serial_number'])


class AssignedEquipment(EquipmentsInSurvey):
    """Proxy model to expose 'equipment assigned to each surveyor' in Admin.

    Shows equipment that are not in store (i.e., currently assigned/with a user).
    """

    class Meta:
        proxy = True
        verbose_name = 'Assigned Equipment (by Surveyor)'
        verbose_name_plural = 'Assigned Equipment (by Surveyor)'


class EquipmentWithoutActivity(EquipmentsInSurvey):
    """Proxy model to list all equipment that have no history entries."""

    class Meta:
        proxy = True
        verbose_name = 'Equipment without Activity'
        verbose_name_plural = 'Equipment without Activity'


