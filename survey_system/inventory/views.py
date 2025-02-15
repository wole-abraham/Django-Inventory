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
from .models import EquipmentsInSurvey
from .forms import Survey

def filter_equipment(request):
    equipment_type = request.GET.get('equipment_type')
    available_equipment = Equipment.objects.filter(equipment_type=equipment_type, status='In Store')  # Ensure only available equipment is returned
    data = [{'id': eq.id, 'name': eq.name} for eq in available_equipment]
    return JsonResponse(data, safe=False)


@login_required
def request_equipment(request):
    if request.method == 'POST':
        equipment_id = request.POST.get('equipment_id')
        if not equipment_id:
            return redirect('request_equipment')  # Redirect back to the form

        try:
            equipment = Equipment.objects.get(id=equipment_id, status='In Store')
        except Equipment.DoesNotExist:
            return redirect('request_equipment')

        # Update equipment status
        surveyor = SurveyorEngineer.objects.get(user=request.user)
        equipment.status = 'In Field'
        equipment.requested_by = request.user
        equipment.save()
        surveyor.requested_equipment.add(equipment)
        return redirect('dashboard')

    available_equipment = Equipment.objects.filter(status='In Store')
    return render(request, 'inventory/request_equipment.html', {'available_equipment': available_equipment})

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


def return_equipment(request):
    if request.method == 'POST':
        equipment_id = request.POST.get('equipment_id')
        equipment = get_object_or_404(Equipment, id=equipment_id, status='In Field', requested_by=request.user)

        # Update equipment status and requested_by field
        equipment.status = 'In Store'
        equipment.requested_by = None
        equipment.save()

        messages.success(request, f'{equipment.name} has been returned successfully.')
        return redirect('dashboard')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Authenticate user
            user = form.get_user()
            login(request, user)
            messages.success(request, 'You have been logged in successfully!')
            return redirect('dashboard')  # Redirect to the dashboard after login
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
        equipment_id = request.POST.get('equipment_id')
        equipment = Equipment.objects.get(id=equipment_id, requested_by=request.user)

        # Mark the equipment as returned by setting requested_by to None
        equipment.status = 'In Store'  # Update the status to 'In Store'
        equipment.requested_by = None  # Remove the user from the equipment
        equipment.save()

        messages.success(request, 'Equipment returned successfully!')
        return redirect('profile')

    return render(request, 'inventory/profile.html', {'user_equipment': user_equipment})

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