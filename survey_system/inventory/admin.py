from django.contrib import admin

# Register your models here.

from .models import  EquipmentsInSurvey, Accessory

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
    list_display = ('name', 'base_serial',)  # Show user details
    
@admin.register(Accessory)
class EquipmentInSurveyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Accessory._meta.fields]