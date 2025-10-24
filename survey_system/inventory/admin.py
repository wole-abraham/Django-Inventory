from django.contrib import admin
from .models import EquipmentsInSurvey, Accessory, Personnel, Chainman

# Register your models here.

# @admin.register(Equipment)
# class EquipmentAdmin(admin.ModelAdmin):
#     list_display = ('name', 'equipment_type', 'status', 'requested_by')  # Display these fields in the list view
#     search_fields = ('name', 'equipment_type')  # Enable search by name and equipment type
#     list_filter = ('status',)  # Filter by status

# Register the SurveyorEngineer model
# @admin.register(SurveyorEngineer)
# class SurveyorEngineerAdmin(admin.ModelAdmin):
#     list_display = ('user',)  # Show user details
#     search_fields = ('user__username', 'first_name', 'last_name')  # Enable search by user, first and last name
@admin.register(EquipmentsInSurvey)
class EquipmentInSurveyAdmin(admin.ModelAdmin):
    list_display = ('name', 'serial_number', 'status', 'chief_surveyor', 'project')
    list_filter = ('status', 'project', 'condition')
    search_fields = ('name', 'serial_number', 'supplier')
    
@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'serial_number', 'equipment', 'status', 'return_status', 'chief_surveyor')
    list_filter = ('status', 'return_status', 'condition')
    search_fields = ('name', 'serial_number')

@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'position', 'department', 'is_active')
    search_fields = ('user__username', 'employee_id', 'position', 'department')
    list_filter = ('department', 'is_active')

@admin.register(Chainman)
class ChainmanAdmin(admin.ModelAdmin):
    list_display = ('name', 'employee_id', 'assigned_to', 'is_active')
    search_fields = ('name', 'employee_id')
    list_filter = ('assigned_to', 'is_active')