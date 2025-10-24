from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
# from .models import Equipment, SurveyorEngineer
from  django.http import JsonResponse, HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import EquipmentsInSurvey, Accessory, Personnel, Chainman
from django.utils import timezone
from .models import EquipmentHistory, AccessoryHistory
from django.db.models import Q
from django.forms import inlineformset_factory

from .forms import Survey, AccessoryForm, AccessoryNoEquipmentForm
from .forms import EquipmentEditForm, CSVUploadForm, AccessoryCSVUploadForm
from .forms import AccessoryEditForm
from .forms import AccessoryReturnForm
from .forms import addEquipmentForm
from .forms import AccessoryQuantityForm
from .forms import PersonnelForm, ChainmanForm, AssignChainmanForm
from .forms import CSVUploadForm
import csv
import io
from datetime import datetime
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch


def get_relevant_accessories(equipment):
    """Get accessories that are relevant to the equipment type"""
    equipment_type = equipment.name.lower()
    relevant_accessory_names = []
    
    if 'gps' in equipment_type or 'gnss' in equipment_type:
        relevant_accessory_names = [
            'Tracking Rod', 'Tripod', 'External Radio', 'GNSS Battery', 
            'Pole', 'GPS Extension Bar', 'External Radio Antenna', 'Data Logger'
        ]
    elif 'total station' in equipment_type:
        relevant_accessory_names = [
            'Reflector', 'Tripod', 'Total Station Prism', 'Mini Prism'
        ]
    elif 'levelling' in equipment_type or 'level' in equipment_type:
        relevant_accessory_names = [
            'Levelling Staff', 'Tripod'
        ]
    else:
        # For other equipment types, show all accessories
        relevant_accessory_names = [
            'Tracking Rod', 'Tripod', 'External Radio', 'Car battery', 'Base pole',
            'Tribrach', 'Reflector', 'Levelling Staff', 'GNSS Battery', 'Pole',
            'Mini Prism', 'Sheet', 'Total Station Prism', 'Radio', 'GPS Extension Bar',
            'Bar Port', 'Powerbank', 'External Radio Antenna', 'Data Logger'
        ]
    
    return Accessory.objects.filter(
        name__in=relevant_accessory_names,
        return_status__in=['In Store', 'Returned', 'Returning']
    ).order_by('name')

# def filter_equipment(request):
#     equipment_type = request.GET.get('equipment_type')
#     available_equipment = Equipment.objects.filter(equipment_type=equipment_type, status='In Store')  # Ensure only available equipment is returned
#     data = [{'id': eq.id, 'name': eq.name} for eq in available_equipment]
#     return JsonResponse(data, safe=False)



@login_required
def add_equipment(request):
    if request.method == "POST":
        form = addEquipmentForm(request.POST)
        if form.is_valid():
            equipment = form.save(commit=False)
            equipment.status = 'In Store'  # Default status
            equipment.save()
            
            # Log equipment creation history
            equipment.log_history(
                action='created',
                changed_by=request.user,
                new_status='In Store',
                new_condition=equipment.condition,
                comment=f"Equipment created by {request.user.username}"
            )
            
            # Create new accessories for each selected type with specified quantity
            accessory_types = form.cleaned_data.get('accessory_types', [])
            for acc_type in accessory_types:
                quantity = form.cleaned_data.get(f'quantity_{acc_type}', 0)
                for i in range(quantity):
                    accessory = Accessory.objects.create(
                        name=acc_type,
                        equipment=equipment,
                        condition='Good',  # Default condition
                        status='Good',  # Default status
                        return_status='In Store',
                    )
                    # Log accessory creation
                    accessory.log_history(
                        action='created',
                        changed_by=request.user,
                        new_status='Good',
                        new_return_status='In Store',
                        new_equipment=str(equipment),
                        comment=f"Accessory created with equipment by {request.user.username}"
                    )
            
            messages.success(request, f'Equipment "{equipment.name}" added successfully with {len(accessory_types)} accessory types!')
            return redirect('store')
    else:
        form = addEquipmentForm()
    return render(request, 'inventory/add_equipment.html', {"form": form})


@login_required
def request_equipment(request):
    if request.user.is_superuser:
        return redirect('store')  # Redirect superusers to store page
    if request.method == 'POST':
        surveyor = request.POST.get('surveyor_res')
        section = request.POST.get('section')
        equipment_id = request.POST.get('id')
        equipment = get_object_or_404(EquipmentsInSurvey, id=equipment_id)
        project = equipment.project
        date = equipment.date_receiving_from_department

        # Update equipment status and assign to user
        equipment.status = 'In Field'
        equipment.section = section
        equipment.date_receiving_from_department = date
        equipment.project = project
        equipment.surveyor_responsible = surveyor
        equipment.chief_surveyor = request.user
        
        equipment.save()
        
        return redirect('profile')
    user = request.user
    data = EquipmentsInSurvey.objects.filter(chief_surveyor=user, status='With Chief Surveyor')
    # Only show accessories that are assigned to the user and not in use or returning (exclude returned)
    accessories = Accessory.objects.filter(
        Q(chief_surveyor=user, return_status='With Chief Surveyor') |
        Q(equipment__chief_surveyor=user, return_status__in=['In Use', 'With Chief Surveyor', 'Delivering'])
    ).exclude(return_status='Returned')
    
    # Serialize accessories data for JavaScript
    accessories_data = []
    for accessory in accessories:
        accessories_data.append({
            'id': accessory.id,
            'name': accessory.name,
            'serial_number': accessory.serial_number,
            'condition': accessory.condition,
            'return_status': accessory.return_status,
            'equipment': {
                'id': accessory.equipment.id if accessory.equipment else None,
                'name': accessory.equipment.name if accessory.equipment else None
            }
        })
    
    return render(request, 'inventory/request_equipment.html', {
        'data': data, 
        'accessories': accessories,
        'accessories_json': json.dumps(accessories_data)
    })

# @receiver(post_save, sender=User)
# def create_surveyor_for_user(sender, instance, created, **kwargs):
#     if created:
#         SurveyorEngineer.objects.create(user=instance)

# @login_required
# def dashboard_view(request):
#     # Query all equipment
#     all_equipment = Equipment.objects.all()

#     return render(request, 'inventory/dashboard.html', {
#         'all_equipment': all_equipment,
#     })

@login_required
def store(request):
    if request.method == 'POST':
        chief_id = request.POST.get('id')
        equipment_id = request.POST.get('equipment_id')
        selected_accessories = request.POST.getlist('selected_accessories')
        
        user = User.objects.filter(id=chief_id).first()
        
        # Check if we're assigning just accessories (no equipment selected)
        if not equipment_id and selected_accessories:
            assigned_count = 0
            for accessory_id in selected_accessories:
                accessory = Accessory.objects.filter(id=accessory_id).first()
                if accessory:
                    # Assign accessory without linking to equipment
                    accessory.mark_as_assigned(user, assigned_by=request.user, equipment_status='Delivering', equipment=None)
                    assigned_count += 1
            
            if assigned_count > 0:
                messages.success(request, f'{assigned_count} accessories assigned to {user.username}.')
            return redirect('store')
            
        # If equipment is selected, proceed with equipment and accessories assignment
        equipment = EquipmentsInSurvey.objects.filter(id=equipment_id).first()
        
        # Update equipment
        equipment.project = request.POST.get("project")
        equipment.chief_surveyor = user
        equipment.delivery_status = "Delivering"
        equipment.status = "Delivering"
        equipment.date_receiving_from_department = timezone.now().date()
        equipment.save()
        
        # Assign selected accessories
        assigned_count = 0
        for accessory_id in selected_accessories:
            accessory = Accessory.objects.filter(id=accessory_id).first()
            if accessory:
                # Link accessory to the equipment and assign to user
                accessory.mark_as_assigned(user, assigned_by=request.user, equipment_status='Delivering', equipment=equipment)
                assigned_count += 1
        
        if assigned_count > 0:
            messages.success(request, f'Equipment {equipment.name} and {assigned_count} accessories assigned to {user.username}.')
        else:
            messages.success(request, f'Equipment {equipment.name} has been released to {user.username}.')
        
        return redirect('store')
    
    users = User.objects.filter(is_superuser=False)
    data = EquipmentsInSurvey.objects.filter(status="In Store")
    all = EquipmentsInSurvey.objects.all()
    accessories = Accessory.objects.filter(return_status__in=['In Store', 'Returned', 'Returning'])
    
    # Get available accessories for assignment (all accessories for general use)
    available_accessories = Accessory.objects.filter(
        return_status__in=['In Store', 'Returned', 'Returning']
    ).order_by('name')
    
    return render(request, 'inventory/store.html', {
        'data': data, 
        'user': users, 
        'all': all,
        'accessories': accessories, 
        'available_accessories': available_accessories,
        'is_admin': request.user.is_superuser
    })

@login_required
def store_all(request):
    data = EquipmentsInSurvey.objects.select_related('chief_surveyor').all()
    return render(request, 'inventory/store_all.html', {'data': data})

@login_required
def store_field(request):
    data = EquipmentsInSurvey.objects.select_related('chief_surveyor').filter(status__in=['In Field', 'With Chief Surveyor'])
    accessories = Accessory.objects.select_related('chief_surveyor', 'equipment').all()
    return render(request, 'inventory/store_field.html', {'data': data, 'accessories': accessories})



@login_required
def return_equipment(request, id):
    equipment = get_object_or_404(EquipmentsInSurvey, id=id)
    
    # Check if user has permission to return this equipment
    if not request.user.is_superuser and equipment.chief_surveyor != request.user:
        messages.error(request, 'You do not have permission to return this equipment.')
        return redirect('profile')
    
    # Get accessories that are linked to this equipment and can be returned
    if request.user.is_superuser:
        # Admin can see all accessories for this equipment
        active_accessories = equipment.accessories.filter(
            return_status__in=['In Use', 'With Chief Surveyor', 'Delivering']
        )
    else:
        # Regular users can only see accessories assigned to them
        active_accessories = equipment.accessories.filter(
            return_status__in=['In Use', 'With Chief Surveyor', 'Delivering'],
            chief_surveyor=request.user
        )
    
    if request.method == 'POST':
        # Check if any accessories are being returned
        accessories_being_returned = False
        for accessory in active_accessories:
            if f'accessory_{accessory.id}' in request.POST:
                accessories_being_returned = True
                break
        
        # Only update equipment status if explicitly requested
        if 'return_equipment' in request.POST:
            equipment.status = 'Returning'
            # Update equipment condition and comment if provided
            equipment_condition = request.POST.get('equipment_condition')
            equipment_comment = request.POST.get('equipment_comment')
            if equipment_condition:
                equipment.condition = equipment_condition
            if equipment_comment:
                equipment.return_comment = equipment_comment
            # Don't remove the chief_surveyor information
            equipment.save()
        
        # Update accessories
        for accessory in active_accessories:
            accessory_id = str(accessory.id)
            if f'accessory_{accessory_id}' in request.POST:  # If accessory is checked for return
                status = request.POST.get(f'accessory_{accessory_id}_status')
                comment = request.POST.get(f'accessory_{accessory_id}_comment')
                
                
                accessory.status = status
                accessory.comment = comment
                accessory.mark_as_returned(request.user)  # Mark as returned with timestamp and user
                accessory.save()
        
        if accessories_being_returned and 'return_equipment' in request.POST:
            messages.success(request, f'{equipment.name} and selected accessories have been returned successfully.')
        elif accessories_being_returned:
            messages.success(request, 'Selected accessories have been returned successfully.')
        elif 'return_equipment' in request.POST:
            messages.success(request, f'{equipment.name} has been marked for return.')
        return redirect('equipment_detail', id=equipment.id)
    
    return render(request, 'equipments/return_equipment.html', {
        'equipment': equipment,
        'active_accessories': active_accessories
    })


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Authenticate user
            user = form.get_user()
            login(request, user)
            messages.success(request, 'You have been logged in successfully!')
            print(f"{user.is_superuser}")
            if user.is_superuser:
                return redirect('store')
            else:
                return redirect('')  # Redirect to the dashboard after login
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        # Handle equipment return with details
        equipment_id = request.POST.get('equipment_id')
        return_comment = request.POST.get('return_comment', '')
        equipment_condition = request.POST.get('equipment_condition', 'Good')
        
        if equipment_id:
            equipment = EquipmentsInSurvey.objects.filter(id=equipment_id).first()
            if equipment:
                # Mark the equipment as returned with details
                equipment.status = 'Returning'
                equipment.condition = equipment_condition
                equipment.return_comment = return_comment
                equipment.return_date = timezone.now()
                equipment.save()
                
                messages.success(request, f'{equipment.name} return request submitted successfully!')
            else:
                messages.error(request, 'Equipment not found.')
        else:
            messages.error(request, 'No equipment selected for return.')
        
        return redirect('profile')
    
    user = request.user
    data = EquipmentsInSurvey.objects.filter(chief_surveyor=user, status__in=['In Field'])
    return render(request, 'inventory/profile.html', {'data':data})


@login_required
def bulk_return_equipment(request):
    """View for bulk returning multiple equipment items"""
    if request.method == 'POST':
        equipment_ids = request.POST.getlist('equipment_ids')
        return_comment = request.POST.get('bulk_return_comment', '')
        equipment_condition = request.POST.get('bulk_equipment_condition', 'Good')
        
        if equipment_ids:
            returned_count = 0
            for equipment_id in equipment_ids:
                equipment = EquipmentsInSurvey.objects.filter(
                    id=equipment_id, 
                    chief_surveyor=request.user, 
                    status='In Field'
                ).first()
                
                if equipment:
                    equipment.status = 'Returning'
                    equipment.condition = equipment_condition
                    equipment.return_comment = return_comment
                    equipment.return_date = timezone.now()
                    equipment.save()
                    
                    returned_count += 1
            
            if returned_count > 0:
                messages.success(request, f'{returned_count} equipment item(s) return request(s) submitted successfully!')
            else:
                messages.error(request, 'No valid equipment found to return.')
        else:
            messages.error(request, 'No equipment selected for return.')
        
        return redirect('profile')
    
    # GET request - show bulk return form
    user = request.user
    data = EquipmentsInSurvey.objects.filter(chief_surveyor=user, status__in=['In Field'])
    return render(request, 'inventory/bulk_return_equipment.html', {'data': data})

def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')  # Redirect to login page or dashboard
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/create_user.html', {'form': form})

# def equipment_in_store(request):
#     """API endpoint for equipment in store."""
#     equipment = Equipment.objects.filter(status='In Store')
#     data = [
#         {
#             'id': eq.id,
#             'name': eq.name,
#             'equipment_type': eq.equipment_type,
#         }
#         for eq in equipment
#     ]
#     return JsonResponse(data, safe=False)

# def equipment_in_field(request):
#     """API endpoint for equipment in the field."""
#     equipment = Equipment.objects.filter(status='In Field')
#     data = [
#         {
#             'id': eq.id,
#             'name': eq.name,
#             'equipment_type': eq.equipment_type,
#             'requested_by': eq.requested_by.username if eq.requested_by else None,
#         }
#         for eq in equipment
#     ]
#     return JsonResponse(data, safe=False)

@login_required
def equipment(request):
    user = request.user
    data = EquipmentsInSurvey.objects.select_related('chief_surveyor').filter(chief_surveyor=user)
    
    return render(request, 'equipments/equipments.html', {'form': Survey, 'data': data})

@login_required
def accessory(request, id):
    equipment = get_object_or_404(EquipmentsInSurvey, id=id)
    
    # Check if user is an admin
    if not request.user.is_superuser:
        messages.error(request, 'Only administrators can add accessories.')
        return redirect('equipment_detail', id=equipment.id)
    
    if request.method == 'POST':
        form = AccessoryForm(request.POST, equipment=equipment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Accessory added successfully!')
            return redirect('equipment_detail', id=equipment.id)
    else:
        form = AccessoryForm(equipment=equipment)
    
    return render(request, 'equipments/accessory.html', {
        'form': form,
        'equipment': equipment
    })

@login_required
def equipment_detail(request, id):
    equipment = get_object_or_404(EquipmentsInSurvey, id=id)
    
    # Check if user has permission to view this equipment
    if not request.user.is_superuser:
        # Regular users can only see equipment they are assigned to or equipment in store
        if equipment.chief_surveyor != request.user and equipment.status != 'In Store':
            messages.error(request, 'You do not have permission to view this equipment.')
            return redirect('profile')
    
    # Handle accessory return form submission
    if request.method == 'POST' and 'return_accessories' in request.POST:
        returned_count = 0
        for key, value in request.POST.items():
            if key.startswith('accessory_') and not key.endswith('_status') and not key.endswith('_comment'):
                accessory_id = value
                accessory = equipment.accessories.filter(id=accessory_id, chief_surveyor=request.user).first()
                if accessory:
                    # Update accessory status and comment
                    status_key = f'accessory_{accessory_id}_status'
                    comment_key = f'accessory_{accessory_id}_comment'
                    
                    accessory.status = request.POST.get(status_key, 'Good')
                    accessory.comment = request.POST.get(comment_key, '')
                    accessory.mark_as_returned(request.user)
                    accessory.save()
                    returned_count += 1
        
        if returned_count > 0:
            messages.success(request, f'{returned_count} accessory(ies) returned successfully!')
        else:
            messages.warning(request, 'No accessories were selected for return.')
        
        return redirect('equipment_detail', id=equipment.id)
    
    # Show accessories assigned to this equipment
    if not request.user.is_superuser:
        # Regular users see accessories assigned to them for this equipment
        active_accessories = equipment.accessories.filter(
            return_status__in=['In Use', 'With Chief Surveyor'],
            chief_surveyor=request.user
        )
        returned_accessories = equipment.accessories.filter(
            return_status__in=['Returned', 'Returning'],
            chief_surveyor=request.user
        )
    else:
        # Admins can see all accessories for this equipment
        active_accessories = equipment.accessories.filter(return_status__in=['In Use', "In Store", "With Chief Surveyor"])
        returned_accessories = equipment.accessories.filter(return_status__in=['Returned', 'Returning'])
    
    return render(request, 'equipments/equipments_detail.html', {
        'equipment': equipment,
        'active_accessories': active_accessories,
        'returned_accessories': returned_accessories
    })

@login_required
def delete_equipment(request, id):
    """Delete equipment and all its accessories"""
    equipment = get_object_or_404(EquipmentsInSurvey, id=id)
    
    # Only allow superusers to delete equipment
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete equipment.')
        return redirect('equipment_detail', id=id)
    
    if request.method == 'POST':
        equipment_name = equipment.name
        equipment_serial = equipment.serial_number
        
        # Delete all accessories first (they have foreign key to equipment)
        accessories_count = equipment.accessories.count()
        equipment.accessories.all().delete()
        
        # Delete the equipment
        equipment.delete()
        
        messages.success(request, f'Equipment "{equipment_name}" (Serial: {equipment_serial}) and its {accessories_count} accessories have been deleted successfully.')
        return redirect('store')
    
    # GET request - show confirmation
    return render(request, 'equipments/delete_equipment.html', {
        'equipment': equipment
    })
def accessory_detail(request, id):
    equipment = get_object_or_404(Accessory, id=id)
    return render(request, 'equipments/accessory_detail.html', {
        'accessory': equipment,
    })

@login_required
def edit_equipment(request, id):
    equipment = get_object_or_404(EquipmentsInSurvey, id=id)
    
    if request.method == 'POST':
        form = EquipmentEditForm(request.POST, request.FILES, instance=equipment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipment details updated successfully!')
            return redirect('equipment_detail', id=equipment.id)
    else:
        form = EquipmentEditForm(instance=equipment)
    
    return render(request, 'equipments/edit_equipment.html', {
        'form': form,
        'equipment': equipment
    })

@login_required
def edit_accessory(request, id):
    accessory = get_object_or_404(Accessory, id=id)
    
    if request.method == 'POST':
        form = AccessoryEditForm(request.POST, request.FILES, instance=accessory)
        if form.is_valid():
            form.save()
            messages.success(request, 'Accessory details updated successfully!')
            return redirect('equipment_detail', id=accessory.equipment.id)
    else:
        form = AccessoryEditForm(instance=accessory)
    
    return render(request, 'equipments/edit_accessory.html', {
        'form': form,
        'accessory': accessory,
        'equipment': accessory.equipment
    })

@login_required
def reset_all_to_store(request):
    """Super button to reset all equipment and accessories to store - only for user 'wole'"""
    if request.user.username != 'wole':
        messages.error(request, 'Access denied. This function is only available to the system administrator.')
        return redirect('store')
    
    if request.method == 'POST':
        # Reset all equipment to "In Store"
        equipment_count = EquipmentsInSurvey.objects.exclude(status='In Store').count()
        EquipmentsInSurvey.objects.exclude(status='In Store').update(
            status='In Store',
            chief_surveyor=None,
            surveyor_responsible='',
            delivery_status=None,
            return_comment=''
        )
        
        # Reset all accessories to "In Store"
        accessory_count = Accessory.objects.exclude(return_status='In Store').count()
        Accessory.objects.exclude(return_status='In Store').update(
            return_status='In Store',
            chief_surveyor=None,
            surveyor_responsible='',
            equipment=None,
            date_assigned=None,
            date_returned=None,
            assigned_by=None,
            returned_by=None,
            comment=''
        )
        
        messages.success(request, f'Reset complete! {equipment_count} equipment and {accessory_count} accessories have been returned to store.')
        return redirect('store')
    
    # Get statistics for the confirmation page
    equipment_in_store = EquipmentsInSurvey.objects.filter(status='In Store').count()
    equipment_assigned = EquipmentsInSurvey.objects.exclude(status='In Store').count()
    accessories_in_store = Accessory.objects.filter(return_status='In Store').count()
    accessories_assigned = Accessory.objects.exclude(return_status='In Store').count()
    
    return render(request, 'inventory/reset_confirm.html', {
        'equipment_in_store': equipment_in_store,
        'equipment_assigned': equipment_assigned,
        'accessories_in_store': accessories_in_store,
        'accessories_assigned': accessories_assigned,
    })

@login_required
def store_returning(request):
    if request.method == 'POST':
        # Handle equipment return
        if 'id' in request.POST:
            equipment_id = request.POST.get('id')
            equipment = EquipmentsInSurvey.objects.filter(id=equipment_id).first()
            equipment.status = 'In Store'
            equipment.chief_surveyor = None  # Clear the chief surveyor assignment
            equipment.save()
            messages.success(request, f'{equipment.name} has been marked as In Store.')
            return redirect('store_returning')
        
        # Handle accessory return
        if 'accessory_id' in request.POST:
            accessory_id = request.POST.get('accessory_id')
            accessory = Accessory.objects.filter(id=accessory_id).first()
            accessory.return_status = 'Returned'
            # Deassign from equipment to make it available again
            accessory.equipment = None
            accessory.chief_surveyor = None
            accessory.surveyor_responsible = None
            accessory.save()
            messages.success(request, f'{accessory.name} has been marked as Available.')
            return redirect('store_returning')

    if request.user.is_superuser:
        # Admin sees all returning items
        data = EquipmentsInSurvey.objects.filter(status='Returning')
        accessories_data = Accessory.objects.filter(return_status='Returning')
    else:
        # Normal users see items they have returned
        data = EquipmentsInSurvey.objects.filter(
            status='Returning',
            chief_surveyor=request.user
        )
        accessories_data = Accessory.objects.filter(
            return_status='Returning',
            returned_by=request.user
        )

    return render(request, 'inventory/store_returning.html', {
        'data': data,
        'accessories': accessories_data,
        'is_admin': request.user.is_superuser
    })


@login_required
def return_accessory(request, id):
    accessory = get_object_or_404(Accessory, id=id)
    
    if request.method == 'POST':
        # Update status and comment
        accessory.status = request.POST.get('status')
        accessory.comment = request.POST.get('comment', '')
        
        # Mark as returned - this will set returned_by and date_returned
        accessory.mark_as_returned(request.user)
        accessory.save()
        
        messages.success(request, f'{accessory.name} has been returned successfully.')
        if accessory.equipment:
            return redirect('equipment_detail', id=accessory.equipment.id)
        else:
            return redirect('profile')
    
    return render(request, 'inventory/return_accessory.html', {
        'accessory': accessory,
        'equipment': accessory.equipment
    })

def release_accessory(request):
    if request.method == 'POST':
        surveyor_responsible = request.POST.get('surveyor_responsible')
        accessory_id = request.POST.get('accessory_id')
        accessory = get_object_or_404(Accessory, id=accessory_id)
        
        # Update surveyor responsible and mark as assigned
        accessory.surveyor_responsible = surveyor_responsible
        accessory.mark_as_assigned(request.user, assigned_by=request.user, equipment_status='With Chief Surveyor', equipment=accessory.equipment)
        
        messages.success(request, f'Accessory {accessory.name} has been released to {surveyor_responsible}.')
        return redirect('profile')

def admin_release_accessory(request):
    if request.method == 'POST':
        user_id = request.POST.get("id")
        accessory_id = request.POST.get('accessory_id')
        user = User.objects.filter(id=user_id).first()
        accessory = get_object_or_404(Accessory, id=accessory_id)
        status = request.POST.get('condition')

        if user:
            accessory.mark_as_assigned(user, assigned_by=request.user, equipment_status='Delivering', equipment=None)
            messages.success(request, f'Accessory {accessory.name} has been assigned to {user.username}.')
            return redirect('store')
        else:
            # Update both status and return_status
            if status:
                accessory.status = status
                accessory.condition = status
                # If changing to "Good", set return_status to "In Store" if it was "Returned"
                if status == 'Good' and accessory.return_status == 'Returned':
                    accessory.return_status = 'In Store'
                # If changing to "Bad" or "Needs Repair", keep current return_status
                accessory.save()
                messages.success(request, f'Accessory {accessory.name} status updated to {status}.')
            else:
                messages.error(request, 'No status selected.')
            
            return redirect('store')
    


@login_required
@login_required
def equipment_history(request, id):
    equipment = get_object_or_404(EquipmentsInSurvey, id=id)
    history = equipment.history.all().order_by('-changed_at')
    
    return render(request, 'inventory/history/equipment_history.html', {
        'equipment': equipment,
        'history': history
    })

@login_required
def accessory_history(request, id):
    accessory = get_object_or_404(Accessory, id=id)
    history = accessory.history.all().order_by('-changed_at')
    
    return render(request, 'inventory/history/accessory_history.html', {
        'accessory': accessory,
        'history': history
    })

@login_required
def all_history(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to view all history.')
        return redirect('login')
    
    # Get all history entries ordered by most recent
    equipment_history = EquipmentHistory.objects.all().order_by('-changed_at')
    accessory_history = AccessoryHistory.objects.all().order_by('-changed_at')
    
    # Combine and sort all history entries
    all_history = list(equipment_history) + list(accessory_history)
    all_history.sort(key=lambda x: x.changed_at, reverse=True)
    
    return render(request, 'inventory/history/all_history.html', {
        'history': all_history
    })

def remove_from_equipment(request, id):
    access = Accessory.objects.filter(id=id).first()
    access.equipment = None
    access.return_status = "Returned"
    access.save()
    return redirect(request.META.get("HTTP_REFERER", "/"))

def delivery(request):
    """View for showing and managing deliveries. Users can only see their own deliveries."""
    
    if request.user.is_superuser:
        eq = EquipmentsInSurvey.objects.filter(status="Delivering")
        # Get all delivering accessories, regardless of equipment association
        accessories = Accessory.objects.filter(
            Q(return_status='Delivering')  # All accessories being delivered
        )
    else:
        eq = EquipmentsInSurvey.objects.filter(status="Delivering", chief_surveyor=request.user)
        # Get only accessories assigned to this user
        accessories = Accessory.objects.filter(
            Q(return_status='Delivering', chief_surveyor=request.user)  # User's delivering accessories
        )
    
    # Serialize accessories data for JavaScript
    accessories_data = []
    for accessory in accessories:
        accessories_data.append({
            'id': accessory.id,
            'name': accessory.name,
            'serial_number': accessory.serial_number,
            'condition': accessory.condition,
            'return_status': accessory.return_status,
            'equipment': {
                'id': accessory.equipment.id if accessory.equipment else None,
                'name': accessory.equipment.name if accessory.equipment else None
            }
        })
    
    return render(request, 'inventory/deliveries.html', {
        "data": eq, 
        "accessories": accessories,
        "accessories_json": json.dumps(accessories_data),
        "is_admin": request.user.is_superuser
    })

def cancel_delivery(request, id):
    # Check if this is an equipment or accessory ID
    equipment = EquipmentsInSurvey.objects.filter(id=id).first()
    accessory = Accessory.objects.filter(id=id).first()
    
    if equipment:
        equipment.delivery_status = "Cancelled"
        equipment.status = "In Store"
        equipment.chief_surveyor = None  # Remove assignment
        equipment.save()
        
        # Also cancel delivery of associated accessories
        accessories = Accessory.objects.filter(equipment=equipment, return_status='Delivering')
        for acc in accessories:
            acc.return_status = 'In Store'
            acc.chief_surveyor = None
            acc.save()
        messages.success(request, f'Equipment {equipment.name} delivery has been cancelled.')
    elif accessory:
        accessory.return_status = 'In Store'
        accessory.chief_surveyor = None
        accessory.equipment = None  # Remove equipment association if any
        accessory.save()
        messages.success(request, f'Accessory {accessory.name} delivery has been cancelled.')
    
    return redirect('store')
def delivery_received(request, id):
    """Handle receiving equipment or accessories from delivery."""
    # First try to find as equipment
    equipment = EquipmentsInSurvey.objects.filter(id=id).first()
    if equipment:
        # Check permissions
        if not (equipment.chief_surveyor == request.user or request.user.is_superuser):
            messages.error(request, 'You do not have permission to receive this equipment.')
            return redirect('delivery')
            
        equipment.delivery_status = "Delivered"
        equipment.status = "With Chief Surveyor"
        equipment.save()
        
        # Update accessories status to match equipment
        accessories = Accessory.objects.filter(equipment=equipment, return_status='Delivering')
        for acc in accessories:
            acc.return_status = 'With Chief Surveyor'
            acc.save()
        messages.success(request, f'Equipment {equipment.name} has been received successfully.')
        return redirect('delivery')
    
    # If not equipment, try as accessory
    accessory = Accessory.objects.filter(id=id).first()
    if accessory:
        # Check permissions
        if not (accessory.chief_surveyor == request.user or request.user.is_superuser):
            messages.error(request, 'You do not have permission to receive this accessory.')
            return redirect('delivery')
            
        accessory.return_status = 'With Chief Surveyor'
        accessory.save()
        messages.success(request, f'Accessory {accessory.name} has been received successfully.')
        return redirect('delivery')
    
    messages.error(request, 'Item not found.')
    return redirect('delivery')

@login_required
def add_accessory(request):
    if not request.user.is_superuser:
        messages.error(request, 'Only administrators can add accessories.')
        return redirect('store')
    if request.method == 'POST':
        form = AccessoryNoEquipmentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Accessory added successfully!')
            return redirect('store')
    else:
        form = AccessoryNoEquipmentForm()
    return render(request, 'inventory/add_accessory.html', {'form': form})
def update_accessory_quantities(request):
    accessories = Accessory.objects.all()
    if request.method == 'POST':
        form = AccessoryQuantityForm(request.POST, accessories=accessories)
        if form.is_valid():
            for accessory in accessories:
                if form.cleaned_data.get(f'accessory_{accessory.id}'):
                    quantity = form.cleaned_data.get(f'quantity_{accessory.id}')
                    if quantity is not None:
                        accessory.quantity = quantity
                        accessory.save()
            return redirect('store')  # Redirect to store after bulk accessory creation
    else:
        form = AccessoryQuantityForm(accessories=accessories)
    return render(request, 'inventory/update_accessory_quantities.html', {'form': form, 'accessories': accessories})


# Personnel Management Views
@login_required
def personnel_list(request):
    """View to display all personnel and their assigned chainmen"""
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('store')
    
    personnel = Personnel.objects.filter(is_active=True).prefetch_related('chainmen')
    unassigned_chainmen = Chainman.objects.filter(assigned_to__isnull=True, is_active=True)
    
    context = {
        'personnel': personnel,
        'unassigned_chainmen': unassigned_chainmen,
        'is_admin': request.user.is_superuser
    }
    return render(request, 'inventory/personnel.html', context)


@login_required
def add_personnel(request):
    """View to add new personnel"""
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('store')
    
    if request.method == 'POST':
        form = PersonnelForm(request.POST)
        if form.is_valid():
            personnel = form.save(commit=False)
            # You might want to create a User account here or link to existing user
            personnel.save()
            messages.success(request, f'Personnel {personnel} added successfully.')
            return redirect('personnel_list')
    else:
        form = PersonnelForm()
    
    return render(request, 'inventory/add_personnel.html', {'form': form})


@login_required
def add_chainman(request):
    """View to add new chainman"""
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('store')
    
    if request.method == 'POST':
        form = ChainmanForm(request.POST)
        if form.is_valid():
            chainman = form.save()
            messages.success(request, f'Chainman {chainman} added successfully.')
            return redirect('personnel_list')
    else:
        form = ChainmanForm()
    
    return render(request, 'inventory/add_chainman.html', {'form': form})


@login_required
def assign_chainman(request):
    """View to assign chainmen to personnel"""
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('store')
    
    if request.method == 'POST':
        form = AssignChainmanForm(request.POST)
        if form.is_valid():
            chainman = form.cleaned_data['chainman']
            personnel = form.cleaned_data['personnel']
            
            chainman.assigned_to = personnel
            chainman.save()
            
            messages.success(request, f'{chainman} assigned to {personnel} successfully.')
            return redirect('personnel_list')
    else:
        form = AssignChainmanForm()
    
    return render(request, 'inventory/assign_chainman.html', {'form': form})


@login_required
def unassign_chainman(request, chainman_id):
    """View to unassign chainman from personnel"""
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('store')
    
    chainman = get_object_or_404(Chainman, id=chainman_id)
    personnel_name = chainman.assigned_to
    chainman.assigned_to = None
    chainman.save()
    
    messages.success(request, f'{chainman} unassigned from {personnel_name} successfully.')
    return redirect('personnel_list')


@login_required
def upload_equipment_csv(request):
    """View to upload CSV file and bulk create equipment"""
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('store')
    
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            
            # Read and process CSV file
            try:
                # Decode the file content
                file_data = csv_file.read().decode('utf-8')
                csv_data = csv.reader(io.StringIO(file_data))
                
                created_count = 0
                skipped_count = 0
                error_count = 0
                errors = []
                skipped_items = []
                
                # Check header row first
                header = next(csv_data, None)
                if header is None:
                    messages.error(request, 'CSV file is empty or invalid.')
                    return render(request, 'inventory/upload_csv.html', {'form': form})
                
                # Validate header format (optional but recommended)
                expected_headers = ['Instrument Name', 'Manufacturer/Model', 'Serial Number(s)', 'Condition']
                if len(header) != 4:
                    messages.error(request, f'Invalid CSV format. Expected exactly 4 columns: {", ".join(expected_headers)}. Found {len(header)} columns.')
                    return render(request, 'inventory/upload_csv.html', {'form': form})
                
                # Check if CSV has any data rows
                csv_rows = list(csv_data)
                if not csv_rows:
                    messages.error(request, 'CSV file contains no data rows.')
                    return render(request, 'inventory/upload_csv.html', {'form': form})
                
                for row_num, row in enumerate(csv_rows, start=2):  # Start from row 2 (after header)
                    try:
                        # Strict validation: must have exactly 4 columns
                        if len(row) != 4:
                            errors.append(f"Row {row_num}: Invalid format. Expected exactly 4 columns (Instrument Name, Manufacturer/Model, Serial Number(s), Condition), found {len(row)} columns")
                            error_count += 1
                            continue
                        
                        # Check for empty values in required columns
                        if not all(cell.strip() for cell in row):
                            empty_columns = [i+1 for i, cell in enumerate(row) if not cell.strip()]
                            errors.append(f"Row {row_num}: Empty values found in column(s): {', '.join(map(str, empty_columns))}")
                            error_count += 1
                            continue
                        
                        # Map CSV columns to model fields
                        # CSV format: Instrument Name, Manufacturer/Model, Serial Number(s), Condition
                        equipment_name = row[0].strip() if len(row) > 0 else ''
                        manufacturer = row[1].strip() if len(row) > 1 else ''
                        serial_number = row[2].strip() if len(row) > 2 else ''
                        condition = row[3].strip() if len(row) > 3 else ''
                        
                        # Map equipment name to valid choices
                        name_mapping = {
                            'GNSS': 'GPS Receiver (Base)',
                            'GPS': 'GPS Receiver (Base)', 
                            'GPS Base': 'GPS Receiver (Base)',
                            'GPS Receiver (Base)': 'GPS Receiver (Base)',
                            'GPS Rover': 'GPS Receiver (Rover)',
                            'GPS Receiver (Rover)': 'GPS Receiver (Rover)',
                            'Total Station': 'Total Station',
                            'Levelling Instrument': 'Levelling Instrument',
                            'Level Instrument': 'Levelling Instrument',
                            'Leveling Instrument': 'Levelling Instrument',
                            'Data logger': 'Data logger',
                            'Data Logger': 'Data logger',
                            'External Radio': 'External Radio',
                            'Radio': 'External Radio',
                            'Eco Sounder': 'Eco Sounder',
                        }
                        
                        # Map manufacturer/supplier name to valid choices
                        supplier_mapping = {
                            'Hi-Target': 'Hi Target',
                            'Hi Target': 'Hi Target',
                            'HiTarget': 'Hi Target',
                            'Topcon': 'Topcon',
                            'Topcon OS-200 Series': 'Topcon OS-200 Series',
                            'Topcon OS 103': 'Topcon OS 103',
                            'Topcon Hiper VR': 'Topcon Hiper VR',
                            'Leica': 'Leica',
                            'Leica NA730 plus': 'Leica NA730 plus',
                            'Sokkia': 'Sokkia',
                            'Hi Target V200': 'Hi Target V200',
                        }
                        
                        # Map condition to valid choices
                        condition_mapping = {
                            'Good': 'Good',
                            'good': 'Good',
                            'GOOD': 'Good',
                            'New': 'New',
                            'new': 'New',
                            'NEW': 'New',
                            'Second Hand': 'Second Hand',
                            'second hand': 'Second Hand',
                            'Used': 'Second Hand',
                            'used': 'Second Hand',
                            'Needs Repair': 'Needs Repair',
                            'needs repair': 'Needs Repair',
                            'Repair': 'Needs Repair',
                            'repair': 'Needs Repair',
                            'Bad': 'Needs Repair',
                            'bad': 'Needs Repair',
                            'Needs Calibration': 'Needs Calibration',
                            'needs calibration': 'Needs Calibration',
                            'Calibration': 'Needs Calibration',
                            'calibration': 'Needs Calibration',
                        }
                        
                        mapped_name = name_mapping.get(equipment_name, equipment_name)
                        mapped_supplier = supplier_mapping.get(manufacturer, manufacturer)
                        mapped_condition = condition_mapping.get(condition, 'Good')  # Default to Good if not found
                        
                        equipment_data = {
                            'name': mapped_name,
                            'supplier': mapped_supplier,
                            'serial_number': serial_number,
                            'owner': 'Hi-Tech',  # Default owner
                            'condition': mapped_condition,
                            'quantity': 1,  # Default quantity to 1
                        }
                        
                        # Validate required fields
                        if not equipment_data['name'] or not equipment_data['serial_number']:
                            errors.append(f"Row {row_num}: Missing required fields (name or serial_number)")
                            error_count += 1
                            continue
                        
                        # Validate that the mapped name is in valid choices
                        valid_equipment_names = [choice[0] for choice in EquipmentsInSurvey.EQUIPMENT_CHOICES]
                        if equipment_data['name'] not in valid_equipment_names:
                            errors.append(f"Row {row_num}: Invalid equipment name '{equipment_data['name']}'. Valid options: {', '.join(valid_equipment_names)}")
                            error_count += 1
                            continue
                        
                        # Supplier validation removed - now accepts any manufacturer/model from CSV
                        
                        # Check if equipment with this serial number already exists
                        existing_equipment = EquipmentsInSurvey.objects.filter(serial_number=equipment_data['serial_number']).first()
                        if existing_equipment:
                            skipped_items.append(f"Serial: {equipment_data['serial_number']} ({equipment_data['name']})")
                            skipped_count += 1
                            continue
                        
                        # Create equipment
                        equipment = EquipmentsInSurvey.objects.create(**equipment_data)
                        created_count += 1
                        
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                        error_count += 1
                
                # Display results
                total_processed = created_count + skipped_count + error_count
                
                # Show success message for created items
                if created_count > 0:
                    messages.success(request, f'Successfully created {created_count} new equipment items.')
                
                # Show info message for skipped items (existing equipment)
                if skipped_count > 0:
                    skipped_message = f'{skipped_count} items already exist and were skipped:\n' + '\n'.join(skipped_items[:10])
                    if len(skipped_items) > 10:
                        skipped_message += f'\n... and {len(skipped_items) - 10} more items.'
                    messages.info(request, skipped_message)
                
                # Show error message for invalid rows
                if error_count > 0:
                    error_message = f'{error_count} rows had errors and were rejected:\n' + '\n'.join(errors[:10])
                    if len(errors) > 10:
                        error_message += f'\n... and {len(errors) - 10} more errors.'
                    messages.error(request, error_message)
                
                # Show summary message
                if total_processed > 0:
                    summary_parts = []
                    if created_count > 0:
                        summary_parts.append(f'{created_count} created')
                    if skipped_count > 0:
                        summary_parts.append(f'{skipped_count} skipped (already exist)')
                    if error_count > 0:
                        summary_parts.append(f'{error_count} errors')
                    
                    summary_message = f'Processing complete: {", ".join(summary_parts)} out of {total_processed} total rows.'
                    if error_count == 0:
                        messages.success(request, summary_message)
                    else:
                        messages.warning(request, summary_message)
                
                # Redirect to store if any items were processed successfully (created or skipped)
                if created_count > 0 or (skipped_count > 0 and error_count == 0):
                    return redirect('store')
                elif total_processed == 0:
                    messages.warning(request, 'No equipment was processed. Please check your CSV format.')
                
                # Stay on upload page if there were only errors or no processing occurred
                return render(request, 'inventory/upload_csv.html', {'form': form})
                    
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
    else:
        form = CSVUploadForm()
    
    return render(request, 'inventory/upload_csv.html', {'form': form})


def download_sample_csv(request):
    """View to download a sample CSV file"""
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('store')
    
    from django.http import HttpResponse
    
    # Create sample CSV content
    csv_content = """Instrument Name,Manufacturer/Model,Serial Number(s),Condition
GPS Receiver (Base),Hi Target V200,VAXJ13847392,Good
GPS Receiver (Rover),Topcon,ROV123456,New
Total Station,Leica,TS789012,Good
Levelling Instrument,Leica NA730 plus,LEI345678,Second Hand
Data logger,Hi Target,DLG901234,Good
External Radio,Topcon OS-200 Series,RAD567890,New
Eco Sounder,Sokkia,ECO123456,Needs Calibration"""
    
    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sample_equipment.csv"'
    return response


@login_required
def upload_accessory_csv(request):
    """View to upload CSV file and bulk create accessories"""
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('store')
    
    if request.method == 'POST':
        form = AccessoryCSVUploadForm(request.POST, request.FILES)
        print(f"Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            print(f"CSV file received: {csv_file.name}, size: {csv_file.size}")
            
            # Read and process CSV file
            try:
                # Reset file pointer to beginning (form validation might have read it)
                csv_file.seek(0)
                # Decode the file content
                file_data = csv_file.read().decode('utf-8')
                print(f"File data length: {len(file_data)}")
                csv_data = csv.reader(io.StringIO(file_data))
                
                created_count = 0
                skipped_count = 0
                error_count = 0
                errors = []
                skipped_items = []
                
                # Check header row first
                header = next(csv_data, None)
                print(f"Header row: {header}")
                if header is None:
                    messages.error(request, 'CSV file is empty or invalid.')
                    return render(request, 'inventory/upload_accessory_csv.html', {'form': form})
                
                # Validate header format
                expected_headers = ['Accessory Name', 'manufacturer', 'Condition']
                print(f"Expected headers: {expected_headers}")
                print(f"Actual headers: {header}")
                print(f"Header length: {len(header)}")
                if len(header) != 3:
                    messages.error(request, f'Invalid CSV format. Expected exactly 3 columns: {", ".join(expected_headers)}. Found {len(header)} columns.')
                    return render(request, 'inventory/upload_accessory_csv.html', {'form': form})
                
                # Check if CSV has any data rows
                csv_rows = list(csv_data)
                print(f"Found {len(csv_rows)} data rows in CSV")
                if not csv_rows:
                    messages.error(request, 'CSV file contains no data rows.')
                    return render(request, 'inventory/upload_accessory_csv.html', {'form': form})
                
                for row_num, row in enumerate(csv_rows, start=2):  # Start from 2 since header is row 1
                    try:
                        # Skip completely empty rows
                        if not any(cell.strip() for cell in row):
                            continue
                            
                        # Strict validation: must have exactly 3 columns
                        if len(row) != 3:
                            errors.append(f"Row {row_num}: Invalid format. Expected exactly 3 columns (Accessory Name, Manufacturer, Condition), found {len(row)} columns")
                            error_count += 1
                            continue
                        
                        # Skip only completely empty rows
                        if not any(cell.strip() for cell in row):
                            print(f"Skipped row {row_num}: completely empty row")
                            continue
                        
                        # Map CSV columns to model fields - accept any content
                        # CSV format: Accessory Name, Manufacturer, Condition
                        accessory_name = row[0].strip() if row[0].strip() else f"Accessory_{row_num}"
                        manufacturer = row[1].strip() if row[1].strip() else "Unknown"
                        condition = row[2].strip() if row[2].strip() else "Good"
                        
                        # Create accessory data dictionary
                        accessory_data = {
                            'name': accessory_name,
                            'manufacturer': manufacturer,
                            'condition': condition,
                            'status': 'Good',  # Default status
                            'return_status': 'In Store',
                        }
                        print(f"Processing row {row_num}: {accessory_name} | {manufacturer} | {condition}")
                        
                        # Validate required fields
                        if not accessory_data['name']:
                            errors.append(f"Row {row_num}: Accessory name cannot be empty")
                            error_count += 1
                            continue
                        
                        # Create accessory
                        accessory = Accessory.objects.create(**accessory_data)
                        created_count += 1
                        print(f"Created accessory: {accessory.name} - {accessory.manufacturer} - {accessory.condition}")
                        
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                        error_count += 1
                
                # Display results
                total_processed = created_count + skipped_count + error_count
                print(f"Final results: {created_count} created, {skipped_count} skipped, {error_count} errors")
                
                # Show success message for created items
                if created_count > 0:
                    messages.success(request, f'Successfully created {created_count} accessories from CSV.')
                
                # Show warning for skipped items
                if skipped_count > 0:
                    messages.warning(request, f'Skipped {skipped_count} accessories (already exist or invalid data).')
                
                # Show error details if any
                if errors:
                    error_message = f'Found {error_count} errors:\n' + '\n'.join(errors[:10])  # Show first 10 errors
                    if len(errors) > 10:
                        error_message += f'\n... and {len(errors) - 10} more errors.'
                    messages.error(request, error_message)
                
                # Show summary
                if total_processed > 0:
                    summary_message = f'Processed {total_processed} rows: {created_count} created, {skipped_count} skipped, {error_count} errors.'
                    if error_count == 0:
                        messages.success(request, summary_message)
                    else:
                        messages.warning(request, summary_message)
                
                # Redirect to store if any items were processed successfully (created or skipped)
                if created_count > 0 or (skipped_count > 0 and error_count == 0):
                    return redirect('store')
                elif total_processed == 0:
                    messages.warning(request, 'No accessories were processed. Please check your CSV format.')
                
                # Stay on upload page if there were only errors or no processing occurred
                return render(request, 'inventory/upload_accessory_csv.html', {'form': form})
                    
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
    else:
        form = AccessoryCSVUploadForm()
    
    return render(request, 'inventory/upload_accessory_csv.html', {'form': form})


def download_sample_accessory_csv(request):
    """View to download a sample accessory CSV file"""
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('store')
    
    from django.http import HttpResponse
    
    # Create sample CSV content
    csv_content = """Accessory Name,manufacturer,Condition
Tripod,Hi Target,Good
Tracking Rod,Topcon,New
External Radio,Leica,Good
Reflector,Sokkia,Second Hand
Levelling Staff,Hi Target,Good
GNSS Battery,Topcon,New
Pole,Leica,Good
Mini Prism,Sokkia,Good"""
    
    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sample_accessories.csv"'
    return response


@login_required
def print_equipment_pdf(request):
    """Generate PDF report of equipment table"""
    # Get equipment data based on user permissions
    if request.user.is_superuser:
        # Admin sees all equipment
        equipment_data = EquipmentsInSurvey.objects.all().order_by('name', 'serial_number')
        accessories_data = Accessory.objects.all().order_by('name', 'serial_number')
    else:
        # Regular users see only their assigned equipment and accessories
        equipment_data = EquipmentsInSurvey.objects.filter(
            chief_surveyor=request.user
        ).order_by('name', 'serial_number')
        accessories_data = Accessory.objects.filter(
            chief_surveyor=request.user
        ).order_by('name', 'serial_number')
    
    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    if request.user.is_superuser:
        filename = f"complete_equipment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    else:
        username = request.user.username.replace(' ', '_')
        filename = f"{username}_equipment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1,  # Center alignment
    )
    
    # Add title based on user type
    if request.user.is_superuser:
        title_text = "Complete Equipment Inventory Report"
    else:
        title_text = f"Equipment Report for {request.user.get_full_name() or request.user.username}"
    
    title = Paragraph(title_text, title_style)
    story.append(title)
    
    # Add report info
    report_info = f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>"
    report_info += f"Generated by: {request.user.get_full_name() or request.user.username}<br/>"
    if request.user.is_superuser:
        report_info += f"Total Equipment: {equipment_data.count()}<br/>"
        report_info += f"Total Accessories: {accessories_data.count()}"
    else:
        report_info += f"Assigned Equipment: {equipment_data.count()}<br/>"
        report_info += f"Assigned Accessories: {accessories_data.count()}"
    
    info_style = ParagraphStyle(
        'ReportInfo',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=20,
    )
    story.append(Paragraph(report_info, info_style))
    story.append(Spacer(1, 12))
    
    # Equipment Table
    if equipment_data.exists():
        if request.user.is_superuser:
            section_title = "All Equipment"
        else:
            section_title = "My Assigned Equipment"
        story.append(Paragraph(section_title, styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Create equipment table data
        equipment_table_data = [['Name', 'Supplier', 'Serial Number', 'Status', 'Condition', 'Chief Surveyor', 'Project']]
        
        for equipment in equipment_data:
            row = [
                equipment.name,
                equipment.supplier,
                equipment.serial_number,
                equipment.status,
                equipment.condition,
                equipment.chief_surveyor.username if equipment.chief_surveyor else 'Unassigned',
                equipment.project or 'N/A'
            ]
            equipment_table_data.append(row)
        
        # Create equipment table
        equipment_table = Table(equipment_table_data, repeatRows=1)
        equipment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(equipment_table)
        story.append(Spacer(1, 20))
    
    # Accessories Table
    if accessories_data.exists():
        if request.user.is_superuser:
            section_title = "All Accessories"
        else:
            section_title = "My Assigned Accessories"
        story.append(Paragraph(section_title, styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Create accessories table data
        accessories_table_data = [['Name', 'Manufacturer', 'Serial Number', 'Condition', 'Status', 'Equipment', 'Equipment Serial']]
        
        for accessory in accessories_data:
            row = [
                accessory.name,
                accessory.manufacturer or 'N/A',
                accessory.serial_number,
                accessory.condition or 'Good',
                accessory.return_status or 'In Store',
                accessory.equipment.name if accessory.equipment else 'Standalone',
                accessory.equipment.serial_number if accessory.equipment else 'N/A'
            ]
            accessories_table_data.append(row)
        
        # Create accessories table with column widths
        accessories_table = Table(accessories_table_data, repeatRows=1, colWidths=[1.2*inch, 1*inch, 1*inch, 0.8*inch, 1*inch, 1.2*inch, 1*inch])
        accessories_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(accessories_table)
    
    # Add message if no data for regular users
    if not request.user.is_superuser and not equipment_data.exists() and not accessories_data.exists():
        story.append(Spacer(1, 20))
        no_data_style = ParagraphStyle(
            'NoData',
            parent=styles['Normal'],
            fontSize=12,
            alignment=1,  # Center alignment
            textColor=colors.grey,
        )
        no_data_msg = Paragraph("No equipment or accessories assigned to you.", no_data_style)
        story.append(no_data_msg)
    
    # Build PDF
    doc.build(story)
    
    return response


@login_required
def equipment_history_pdf(request, id):
    """Export equipment history to PDF"""
    equipment = get_object_or_404(EquipmentsInSurvey, id=id)
    history = equipment.history.all().order_by('-changed_at')
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="equipment_history_{equipment.serial_number}_{timezone.now().strftime("%Y%m%d")}.pdf"'
    
    # Create the PDF object
    doc = SimpleDocTemplate(response, pagesize=A4)
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=1,  # Center alignment
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
    )
    
    # Add title
    title = Paragraph(f"Equipment History Report", title_style)
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Equipment Details
    equipment_info = [
        ['Equipment Name:', equipment.name],
        ['Serial Number:', equipment.serial_number],
        ['Supplier:', equipment.supplier],
        ['Current Status:', equipment.status or 'N/A'],
        ['Current Condition:', equipment.condition or 'Good'],
        ['Current Chief Surveyor:', equipment.chief_surveyor.username if equipment.chief_surveyor else 'N/A'],
        ['Project:', equipment.project or 'N/A'],
        ['Section:', equipment.section or 'N/A'],
    ]
    
    equipment_table = Table(equipment_info, colWidths=[2.5*inch, 4*inch])
    equipment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(equipment_table)
    story.append(Spacer(1, 20))
    
    # History section
    subtitle = Paragraph("History Log", subtitle_style)
    story.append(subtitle)
    story.append(Spacer(1, 12))
    
    if history.exists():
        history_data = [['Date/Time', 'Action', 'Changed By', 'Details']]
        
        for entry in history:
            # Format date
            date_str = entry.changed_at.strftime("%Y-%m-%d %H:%M")
            
            # Get action display
            action_str = entry.get_action_display()
            
            # Get changed by
            changed_by_str = entry.changed_by.username if entry.changed_by else 'System'
            
            # Get description
            description = entry.get_description()
            
            row = [
                date_str,
                action_str,
                changed_by_str,
                Paragraph(description, styles['Normal'])
            ]
            history_data.append(row)
        
        history_table = Table(history_data, repeatRows=1, colWidths=[1.3*inch, 1.5*inch, 1.2*inch, 3.5*inch])
        history_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        
        story.append(history_table)
    else:
        no_history_style = ParagraphStyle(
            'NoHistory',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=1,
        )
        no_history = Paragraph("No history records found for this equipment.", no_history_style)
        story.append(no_history)
    
    # Build PDF
    doc.build(story)
    
    return response


@login_required
def accessory_history_pdf(request, id):
    """Export accessory history to PDF"""
    accessory = get_object_or_404(Accessory, id=id)
    history = accessory.history.all().order_by('-changed_at')
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="accessory_history_{accessory.serial_number}_{timezone.now().strftime("%Y%m%d")}.pdf"'
    
    # Create the PDF object
    doc = SimpleDocTemplate(response, pagesize=A4)
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=1,
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
    )
    
    # Add title
    title = Paragraph(f"Accessory History Report", title_style)
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Accessory Details
    accessory_info = [
        ['Accessory Name:', accessory.name],
        ['Serial Number:', accessory.serial_number or 'N/A'],
        ['Manufacturer:', accessory.manufacturer or 'N/A'],
        ['Current Status:', accessory.status or 'Good'],
        ['Return Status:', accessory.return_status or 'In Store'],
        ['Current Chief Surveyor:', accessory.chief_surveyor.username if accessory.chief_surveyor else 'N/A'],
        ['Linked Equipment:', str(accessory.equipment) if accessory.equipment else 'Standalone'],
    ]
    
    accessory_table = Table(accessory_info, colWidths=[2.5*inch, 4*inch])
    accessory_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(accessory_table)
    story.append(Spacer(1, 20))
    
    # History section
    subtitle = Paragraph("History Log", subtitle_style)
    story.append(subtitle)
    story.append(Spacer(1, 12))
    
    if history.exists():
        history_data = [['Date/Time', 'Action', 'Changed By', 'Details']]
        
        for entry in history:
            date_str = entry.changed_at.strftime("%Y-%m-%d %H:%M")
            action_str = entry.get_action_display()
            changed_by_str = entry.changed_by.username if entry.changed_by else 'System'
            description = entry.get_description()
            
            row = [
                date_str,
                action_str,
                changed_by_str,
                Paragraph(description, styles['Normal'])
            ]
            history_data.append(row)
        
        history_table = Table(history_data, repeatRows=1, colWidths=[1.3*inch, 1.5*inch, 1.2*inch, 3.5*inch])
        history_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        
        story.append(history_table)
    else:
        no_history_style = ParagraphStyle(
            'NoHistory',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=1,
        )
        no_history = Paragraph("No history records found for this accessory.", no_history_style)
        story.append(no_history)
    
    # Build PDF
    doc.build(story)
    
    return response


@login_required
def all_history_pdf(request):
    """Export all history to PDF (Admin only)"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to export all history.')
        return redirect('login')
    
    equipment_history = EquipmentHistory.objects.all().order_by('-changed_at')[:100]  # Limit to last 100
    accessory_history = AccessoryHistory.objects.all().order_by('-changed_at')[:100]  # Limit to last 100
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="all_history_{timezone.now().strftime("%Y%m%d_%H%M")}.pdf"'
    
    # Create the PDF object
    doc = SimpleDocTemplate(response, pagesize=A4)
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=1,
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        spaceBefore=20,
    )
    
    # Add title
    title = Paragraph(f"Complete History Report", title_style)
    story.append(title)
    
    subtitle = Paragraph(f"Generated on {timezone.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal'])
    story.append(subtitle)
    story.append(Spacer(1, 20))
    
    # Equipment History Section
    if equipment_history.exists():
        section_title = Paragraph("Equipment History (Last 100 entries)", section_style)
        story.append(section_title)
        story.append(Spacer(1, 12))
        
        eq_history_data = [['Date/Time', 'Equipment', 'Action', 'Changed By', 'Details']]
        
        for entry in equipment_history:
            date_str = entry.changed_at.strftime("%Y-%m-%d %H:%M")
            equipment_str = f"{entry.equipment.name}\n({entry.equipment.serial_number})"
            action_str = entry.get_action_display()
            changed_by_str = entry.changed_by.username if entry.changed_by else 'System'
            description = entry.get_description()[:100] + '...' if len(entry.get_description()) > 100 else entry.get_description()
            
            row = [
                date_str,
                Paragraph(equipment_str, styles['Normal']),
                action_str,
                changed_by_str,
                Paragraph(description, styles['Normal'])
            ]
            eq_history_data.append(row)
        
        eq_history_table = Table(eq_history_data, repeatRows=1, colWidths=[1.1*inch, 1.3*inch, 1.3*inch, 1*inch, 2.8*inch])
        eq_history_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ]))
        
        story.append(eq_history_table)
        story.append(Spacer(1, 20))
    
    # Accessory History Section
    if accessory_history.exists():
        section_title = Paragraph("Accessory History (Last 100 entries)", section_style)
        story.append(section_title)
        story.append(Spacer(1, 12))
        
        acc_history_data = [['Date/Time', 'Accessory', 'Action', 'Changed By', 'Details']]
        
        for entry in accessory_history:
            date_str = entry.changed_at.strftime("%Y-%m-%d %H:%M")
            accessory_str = f"{entry.accessory.name}\n({entry.accessory.serial_number or 'N/A'})"
            action_str = entry.get_action_display()
            changed_by_str = entry.changed_by.username if entry.changed_by else 'System'
            description = entry.get_description()[:100] + '...' if len(entry.get_description()) > 100 else entry.get_description()
            
            row = [
                date_str,
                Paragraph(accessory_str, styles['Normal']),
                action_str,
                changed_by_str,
                Paragraph(description, styles['Normal'])
            ]
            acc_history_data.append(row)
        
        acc_history_table = Table(acc_history_data, repeatRows=1, colWidths=[1.1*inch, 1.3*inch, 1.3*inch, 1*inch, 2.8*inch])
        acc_history_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ]))
        
        story.append(acc_history_table)
    
    if not equipment_history.exists() and not accessory_history.exists():
        no_history_style = ParagraphStyle(
            'NoHistory',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.grey,
            alignment=1,
        )
        no_history = Paragraph("No history records found.", no_history_style)
        story.append(no_history)
    
    # Build PDF
    doc.build(story)
    
    return response

