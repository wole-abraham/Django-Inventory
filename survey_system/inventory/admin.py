from django.contrib import admin
from django.db.models import Count, OuterRef, Subquery
from django.http import HttpResponse
import csv
from .models import (
    EquipmentsInSurvey,
    Accessory,
    Personnel,
    Chainman,
    EquipmentHistory,
    AccessoryHistory,
    AssignedEquipment,
    EquipmentWithoutActivity,
)

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


def export_as_csv(modeladmin, request, queryset):
    """Generic CSV export admin action."""
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta.model_name}_export.csv'
    writer = csv.writer(response)
    writer.writerow(field_names)
    for obj in queryset:
        row = [getattr(obj, field) for field in field_names]
        writer.writerow(row)
    return response

export_as_csv.short_description = 'Export selected to CSV'


@admin.register(EquipmentHistory)
class EquipmentHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'equipment', 'action', 'new_status', 'new_condition', 'new_chief_surveyor',
        'new_project', 'new_section', 'changed_by', 'changed_at'
    )
    list_filter = (
        'action', 'new_status', 'new_condition', 'new_project', 'new_section', 'changed_by'
    )
    search_fields = (
        'equipment__name', 'equipment__serial_number', 'comment',
        'new_surveyor_responsible', 'previous_surveyor_responsible'
    )
    date_hierarchy = 'changed_at'
    actions = [export_as_csv]


@admin.register(AccessoryHistory)
class AccessoryHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'accessory', 'action', 'new_status', 'new_return_status', 'new_condition',
        'new_chief_surveyor', 'new_equipment', 'changed_by', 'changed_at'
    )
    list_filter = (
        'action', 'new_status', 'new_return_status', 'new_condition', 'changed_by'
    )
    search_fields = (
        'accessory__name', 'accessory__serial_number', 'comment', 'new_equipment'
    )
    date_hierarchy = 'changed_at'
    actions = [export_as_csv]


@admin.register(AssignedEquipment)
class AssignedEquipmentAdmin(admin.ModelAdmin):
    """Report-style admin showing equipment assigned to surveyors."""
    list_display = (
        'name', 'serial_number', 'chief_surveyor', 'project', 'status', 'last_action_time'
    )
    list_filter = ('project', 'status', 'chief_surveyor')
    search_fields = ('name', 'serial_number', 'chief_surveyor__username')
    actions = [export_as_csv]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Consider "assigned" as not in store
        qs = qs.select_related('chief_surveyor').filter(status__in=['In Field', 'With Chief Surveyor'])
        # Annotate last history time for quick display
        last_hist = EquipmentHistory.objects.filter(equipment_id=OuterRef('pk')).order_by('-changed_at').values('changed_at')[:1]
        return qs.annotate(_last_changed_at=Subquery(last_hist))

    @admin.display(description='Last Activity', ordering='_last_changed_at')
    def last_action_time(self, obj):
        return getattr(obj, '_last_changed_at', None)


@admin.register(EquipmentWithoutActivity)
class EquipmentWithoutActivityAdmin(admin.ModelAdmin):
    """All equipment in the company with no activities (no history)."""
    list_display = ('name', 'serial_number', 'project', 'status', 'chief_surveyor')
    list_filter = ('project', 'status')
    search_fields = ('name', 'serial_number')
    actions = [export_as_csv]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # No related history entries
        return qs.select_related('chief_surveyor').annotate(h_count=Count('history')).filter(h_count=0)

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