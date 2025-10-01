from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import EquipmentsInSurvey, Accessory, Personnel, Chainman

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

class Survey(forms.ModelForm):
    class Meta:
        model = EquipmentsInSurvey
        fields = []

class AccessoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        equipment = kwargs.pop('equipment', None)
        super().__init__(*args, **kwargs)
        # Only show type selection
        self.fields['name'] = forms.ChoiceField(
            choices=Accessory.ACCESSORY_TYPES,
            label='Accessory Type',
            widget=forms.Select(attrs={'class': 'form-select'})
        )
        # Remove unwanted fields if present
        for field in ['equipment', 'comment', 'image', 'serial_number']:
            if field in self.fields:
                self.fields.pop(field)
        self.equipment = equipment

    class Meta:
        model = Accessory
        fields = ['name']

    def save(self, commit=True):
        accessory = Accessory(
            name=self.cleaned_data['name'],
            serial_number=self.equipment.serial_number if self.equipment else None,
            equipment=self.equipment,
            return_status='In Store',
        )
        if commit:
            accessory.save()
        return accessory

class AccessoryNoEquipmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
       
        for field in ['equipment', 'comment', 'image']:
            if field in self.fields:
                self.fields.pop(field)

    class Meta:
        model = Accessory
        fields = ['name', 'serial_number']
        widgets = {
            'name': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Select Accessory Type'
            }),
            'serial_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter serial number'
            }),
        }

class EquipmentEditForm(forms.ModelForm):
    class Meta:
        model = EquipmentsInSurvey
        fields = [
            'name', 'date_of_receiving_from_supplier', 'supplier', 
            'serial_number', 'project', 'section', 'date_receiving_from_department'
        ]
        widgets = {
            'date_of_receiving_from_supplier': forms.DateInput(attrs={'type': 'date'}),
            'date_receiving_from_department': forms.DateInput(attrs={'type': 'date'}),
        }

class AccessoryEditForm(forms.ModelForm):
    class Meta:
        model = Accessory
        fields = ['status', 'comment']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Select Status'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter any additional comments',
                'rows': 3
            })
        }

class AccessoryReturnForm(forms.Form):
    def __init__(self, *args, **kwargs):
        equipment = kwargs.pop('equipment', None)
        super(AccessoryReturnForm, self).__init__(*args, **kwargs)
        
        if equipment:
            accessories = equipment.accessories.all()
            for accessory in accessories:
                # Add checkbox field
                self.fields[f'accessory_{accessory.id}'] = forms.BooleanField(
                    required=True,
                    label=f"{accessory.name} - Current Status: {accessory.status}",
                    initial=True,
                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
                )
                
                # Add status field
                self.fields[f'accessory_{accessory.id}_status'] = forms.ChoiceField(
                    choices=Accessory.STATUS_CHOICES,
                    initial=accessory.status,
                    widget=forms.Select(attrs={'class': 'form-select'}),
                    label='Status'
                )
                
                # Add comment field
                self.fields[f'accessory_{accessory.id}_comment'] = forms.CharField(
                    required=False,
                    widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Add any comments about the accessory condition'}),
                    initial=accessory.comment,
                    label='Comments'
                )

                
                # Store accessory ID for easy access in template
                self.fields[f'accessory_{accessory.id}'].accessory_id = accessory.id

class addEquipmentForm(forms.ModelForm):
    accessory_types = forms.MultipleChoiceField(
        choices=Accessory.ACCESSORY_TYPES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Select Accessory Types to Create"
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'chief_surveyor' in self.fields:
            self.fields['chief_surveyor'].queryset = User.objects.filter(is_superuser=False)
        # Add a quantity field for each accessory type, default 0
        for key, label in Accessory.ACCESSORY_TYPES:
            self.fields[f'quantity_{key}'] = forms.IntegerField(
                label=f"Quantity for {label}", min_value=0, initial=0, required=False
            )
    class Meta:
        model = EquipmentsInSurvey
        fields = [
            'name',
            'owner',
            'date_of_receiving_from_supplier',
            'supplier',
            'serial_number',
            'condition',
        ]
        widgets = {
            'date_of_receiving_from_supplier': forms.DateInput(attrs={'type': 'date'}),
            'serial_number': forms.TextInput(attrs={'required': True}),
        }

class AccessoryQuantityForm(forms.Form):
    def __init__(self, *args, **kwargs):
        accessories = kwargs.pop('accessories')
        super().__init__(*args, **kwargs)
        for accessory in accessories:
            self.fields[f'accessory_{accessory.id}'] = forms.BooleanField(
                label=accessory.name, required=False
            )
            self.fields[f'quantity_{accessory.id}'] = forms.IntegerField(
                label='Quantity', min_value=1, initial=accessory.quantity, required=False
            )


class PersonnelForm(forms.ModelForm):
    """Form for creating/editing personnel"""
    class Meta:
        model = Personnel
        fields = ['user', 'employee_id', 'position', 'department', 'phone_number', 'is_active']
        widgets = {
            'phone_number': forms.TextInput(attrs={'type': 'tel', 'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-select'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter out admin users (superusers)
        self.fields['user'].queryset = User.objects.filter(is_superuser=False)
        self.fields['user'].empty_label = "Select User"


class ChainmanForm(forms.ModelForm):
    """Form for creating/editing chainmen"""
    class Meta:
        model = Chainman
        fields = ['name', 'employee_id', 'phone_number', 'assigned_to', 'is_active']
        widgets = {
            'phone_number': forms.TextInput(attrs={'type': 'tel', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = Personnel.objects.filter(is_active=True)
        self.fields['assigned_to'].empty_label = "Select Personnel (Optional)"


class AssignChainmanForm(forms.Form):
    """Form for assigning chainmen to personnel"""
    chainman = forms.ModelChoiceField(
        queryset=Chainman.objects.filter(assigned_to__isnull=True, is_active=True),
        empty_label="Select Chainman to Assign",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    personnel = forms.ModelChoiceField(
        queryset=Personnel.objects.filter(is_active=True),
        empty_label="Select Personnel",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

