from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Equipment, SurveyorEngineer
from  django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import EquipmentsInSurvey, Accessory
from django.utils import timezone

from .forms import Survey, AccessoryForm
from .forms import EquipmentEditForm
from .forms import AccessoryEditForm
from .forms import AccessoryReturnForm

def filter_equipment(request):
    equipment_type = request.GET.get('equipment_type')
    available_equipment = Equipment.objects.filter(equipment_type=equipment_type, status='In Store')  # Ensure only available equipment is returned
    data = [{'id': eq.id, 'name': eq.name} for eq in available_equipment]
    return JsonResponse(data, safe=False)


@login_required
def request_equipment(request):
    if request.method == 'POST':
        surveyor = request.POST.get('surveyor_res')
        section = request.POST.get('section')
        project = request.POST.get('project')
        date = request.POST.get('date_receiving')
        
        equipment = EquipmentsInSurvey.objects.filter(id=request.POST.get('id')).first()

        # Update equipment status and requested_by field
        equipment.status = 'In Field'
        equipment.section = section
        equipment.date_receiving_from_department = date
        equipment.project = project
        equipment.surveyor_responsible = surveyor
        
        equipment.save()
        return redirect('profile')
    user = request.user
    data = EquipmentsInSurvey.objects.filter(chief_surveyor=user, status='With Chief Surveyor')
    accessories = Accessory.objects.filter(chief_surveyor=user)
    users = User.objects.filter(is_superuser=False)
    return render(request, 'inventory/request_equipment.html', {
        'data': data,
        'accessories': accessories,
        'users': users
    })

@receiver(post_save, sender=User)
def create_surveyor_for_user(sender, instance, created, **kwargs):
    if created:
        SurveyorEngineer.objects.create(user=instance)

@login_required
def dashboard_view(request):
    # Query all equipment
    all_equipment = Equipment.objects.all()

    return render(request, 'inventory/dashboard.html', {
        'all_equipment': all_equipment,
    })


def store(request):
    if request.method == 'POST':
        chief_id = request.POST.get('id')
        equipment = request.POST.get('equipment_id')
        user = User.objects.filter(id=chief_id).first()
        equipment = EquipmentsInSurvey.objects.filter(id=equipment).first()
        equipment.chief_surveyor = user
        equipment.status = "With Chief Surveyor"
        equipment.date_receiving_from_department = timezone.now().date()  # Update the date
        equipment.save()
        messages.success(request, f'Equipment {equipment.name} has been released to {user.username}.')
        return redirect('store')
    users = User.objects.filter(is_superuser=False)
    data = EquipmentsInSurvey.objects.filter(status="In Store")
    all = EquipmentsInSurvey.objects.all()
    accessories = Accessory.objects.all()
    return render(request, 'inventory/store.html', {'data':data, 'user': users, 'all': all,
                                                    'accessories': accessories})

def store_all(request):
    data = EquipmentsInSurvey.objects.all()
    return render(request, 'inventory/store_all.html', {'data': data})

def store_field(request):
    data = EquipmentsInSurvey.objects.filter(status__in=['In Field', 'With Chief Surveyor'])
    accessories = Accessory.objects.all()
    return render(request, 'inventory/store_field.html', {'data': data, 'accessories': accessories})



@login_required
def return_equipment(request, id):
    equipment = get_object_or_404(EquipmentsInSurvey, id=id)
    active_accessories = equipment.accessories.filter(return_status='In Use')
    
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
            # Don't remove the chief_surveyor information
            equipment.save()
        
        # Update accessories
        for accessory in active_accessories:
            accessory_id = str(accessory.id)
            if f'accessory_{accessory_id}' in request.POST:  # If accessory is checked for return
                status = request.POST.get(f'accessory_{accessory_id}_status')
                comment = request.POST.get(f'accessory_{accessory_id}_comment')
                
                # Handle image upload
                if f'accessory_{accessory_id}_image' in request.FILES:
                    image = request.FILES[f'accessory_{accessory_id}_image']
                    accessory.image = image
                
                accessory.status = status
                accessory.comment = comment
                accessory.mark_as_returned(request.user)  # Mark as returned with timestamp and user
                accessory.save()
        
        if accessories_being_returned:
            messages.success(request, 'Selected accessories have been returned successfully.')
        if 'return_equipment' in request.POST:
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
    # Get all equipment where the user is the requester
    user_equipment = Equipment.objects.filter(requested_by=request.user)

    if request.method == 'POST':
        equipment_id = request.POST.get('id')
        equipment = EquipmentsInSurvey.objects.filter(id=equipment_id).first()

        # Mark the equipment as returned by setting requested_by to None
         # Remove the user from the equipment
        equipment.save()

        messages.success(request, 'Equipment returned successfully!')
        return redirect('profile')
    user = request.user
    data = EquipmentsInSurvey.objects.filter(chief_surveyor=user, status__in=['In Field'])
    accessories = Accessory.objects.filter(chief_surveyor=user)
    return render(request, 'inventory/profile.html', {'user_equipment': user_equipment, 'data':data, 'accessories': accessories})

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

def equipment_in_store(request):
    """API endpoint for equipment in store."""
    equipment = Equipment.objects.filter(status='In Store')
    data = [
        {
            'id': eq.id,
            'name': eq.name,
            'equipment_type': eq.equipment_type,
        }
        for eq in equipment
    ]
    return JsonResponse(data, safe=False)

def equipment_in_field(request):
    """API endpoint for equipment in the field."""
    equipment = Equipment.objects.filter(status='In Field')
    data = [
        {
            'id': eq.id,
            'name': eq.name,
            'equipment_type': eq.equipment_type,
            'requested_by': eq.requested_by.username if eq.requested_by else None,
        }
        for eq in equipment
    ]
    return JsonResponse(data, safe=False)

def equipment(request):
    user = request.user
    data = EquipmentsInSurvey.objects.filter(chief_surveyor=user)
    
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

def equipment_detail(request, id):
    equipment = get_object_or_404(EquipmentsInSurvey, id=id)
    active_accessories = equipment.accessories.filter(return_status='In Use')
    returned_accessories = equipment.accessories.filter(return_status='Returned')
    
    return render(request, 'equipments/equipments_detail.html', {
        'equipment': equipment,
        'active_accessories': active_accessories,
        'returned_accessories': returned_accessories
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
def store_returning(request):
    if request.method == 'POST':
        equipment_id = request.POST.get('id')
        equipment = EquipmentsInSurvey.objects.filter(id=equipment_id).first()
        equipment.status = 'In Store'
        equipment.save()
        messages.success(request, f'{equipment.name} has been marked as In Store.')
        return redirect('store_returning')
    if request.user.is_superuser:
        data = EquipmentsInSurvey.objects.filter(status='Returning')
        accessories_data = Accessory.objects.filter(equipment__in=data)

    else:
        data = EquipmentsInSurvey.objects.filter(
            status='Returning',
            chief_surveyor=request.user
        ) | EquipmentsInSurvey.objects.filter(
            status='Returning',
            surveyor_responsible=request.user.username
        )
        accessories_data = Accessory.objects.filter(equipment__in=data)

    return render(request, 'inventory/store_returning.html', {'data': data, 'accessories': accessories_data})


def return_accessory(request, id):
    accessory = get_object_or_404(Accessory, id=id)
    accessory.return_status = 'Returned'
    accessory.save()
    return redirect('store_returning')

def release_accessory(request):
    if request.method == 'POST':
        surveyor_responsible = request.POST.get('surveyor_responsible')
        accessory_id = request.POST.get('accessory_id')
        accessory = get_object_or_404(Accessory, id=accessory_id)
        accessory.surveyor_responsible = surveyor_responsible
        accessory.return_status = 'In Use'
        accessory.save()
        messages.success(request, f'Accessory {accessory.name} has been released to {surveyor_responsible}.')
        return redirect('request_equipment')