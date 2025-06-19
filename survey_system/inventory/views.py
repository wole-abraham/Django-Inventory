from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
# from .models import Equipment, SurveyorEngineer
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
from .models import EquipmentHistory, AccessoryHistory
from django.db.models import Q

from .forms import Survey, AccessoryForm
from .forms import EquipmentEditForm
from .forms import AccessoryEditForm
from .forms import AccessoryReturnForm
from .forms import addEquipmentForm

# def filter_equipment(request):
#     equipment_type = request.GET.get('equipment_type')
#     available_equipment = Equipment.objects.filter(equipment_type=equipment_type, status='In Store')  # Ensure only available equipment is returned
#     data = [{'id': eq.id, 'name': eq.name} for eq in available_equipment]
#     return JsonResponse(data, safe=False)



def add_equipment(request):
    if request.method == "POST":
        form = addEquipmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('store')
    else:
        form = addEquipmentForm()
    return render(request, 'inventory/add_equipment.html', {"form": form})


@login_required
def request_equipment(request):
    if request.method == 'POST':
        surveyor = request.POST.get('surveyor_res')
        section = request.POST.get('section')
        equipment = EquipmentsInSurvey.objects.filter(id=request.POST.get('id')).first()
        project = equipment.project
        date = equipment.date_receiving_from_department


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
    # Only show accessories that are assigned to the user and not in use or returning
    accessories = Accessory.objects.filter(
    Q(chief_surveyor=user, return_status='With Chief Surveyor') |
    Q(equipment__chief_surveyor=user)
)
    return render(request, 'inventory/request_equipment.html', {'data':data, 'accessories': accessories})

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


def store(request):
    if request.method == 'POST':
        chief_id = request.POST.get('id')
        equipment = request.POST.get('equipment_id')
        user = User.objects.filter(id=chief_id).first()
        equipment = EquipmentsInSurvey.objects.filter(id=equipment).first()
        equipment.section = request.POST.get("section")
        equipment.chief_surveyor = user
        equipment.delivery_status = "Delivering"
        equipment.status = "Delivering"
        equipment.date_receiving_from_department = request.POST.get("date_receiving") or timezone.now().date()  # Update the date
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
    # user_equipment = Equipment.objects.filter(requested_by=request.user)

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
    accessories = Accessory.objects.filter(chief_surveyor=user, return_status="In Use")
    return render(request, 'inventory/profile.html', {'data':data, 'accessories': accessories})

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
    returned_accessories = equipment.accessories.filter(return_status__in=['Returned', 'Returning'])
    
    return render(request, 'equipments/equipments_detail.html', {
        'equipment': equipment,
        'active_accessories': active_accessories,
        'returned_accessories': returned_accessories
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
def store_returning(request):
    if request.method == 'POST':
        # Handle equipment return
        if 'id' in request.POST:
            equipment_id = request.POST.get('id')
            equipment = EquipmentsInSurvey.objects.filter(id=equipment_id).first()
            equipment.status = 'In Store'
            equipment.save()
            messages.success(request, f'{equipment.name} has been marked as In Store.')
            return redirect('store_returning')
        
        # Handle accessory return
        if 'accessory_id' in request.POST:
            accessory_id = request.POST.get('accessory_id')
            accessory = Accessory.objects.filter(id=accessory_id).first()
            accessory.return_status = 'Returned'
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
        # Handle image upload
        if 'image' in request.FILES:
            accessory.image = request.FILES['image']
        
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
        accessory.surveyor_responsible = surveyor_responsible
        accessory.return_status = 'In Use'
        accessory.save()
        messages.success(request, f'Accessory {accessory.name} has been released to {surveyor_responsible}.')
        return redirect('request_equipment')

def admin_release_accessory(request):
    if request.method == 'POST':
        accessory_id = request.POST.get('accessory_id')
        accessory = get_object_or_404(Accessory, id=accessory_id)
        status  = request.POST.get('condition')
        accessory.status = status
        accessory.save()
        return redirect('store')
    


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
    access.save()
    return redirect(request.META.get("HTTP_REFERER", "/"))

def delivery(request):
    if request.user.is_superuser:
        eq = EquipmentsInSurvey.objects.filter(status="Delivering")
        return render(request, 'inventory/deliveries.html', {"data": eq})
    else:
        eq = EquipmentsInSurvey.objects.filter(status="Delivering", chief_surveyor=request.user)
        return render(request, 'inventory/deliveries.html', {"data": eq})

def cancel_delivery(request, id):
    eq = EquipmentsInSurvey.objects.filter(id=id).first()
    eq.delivery_status = "Cancelled"
    eq.status = "In Store"
    eq.save()
    return redirect('store')
def delivery_received(request, id):
    eq = EquipmentsInSurvey.objects.filter(id=id).first()
    eq.delivery_status = "Received"
    eq.status = "With Chief Surveyor"
    eq.save()
    return redirect('profile')

@login_required
def add_accessory(request):
    if not request.user.is_superuser:
        messages.error(request, 'Only administrators can add accessories.')
        return redirect('store')
    if request.method == 'POST':
        form = AccessoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Accessory added successfully!')
            return redirect('store')
    else:
        form = AccessoryForm()
    return render(request, 'inventory/add_accessory.html', {'form': form})
