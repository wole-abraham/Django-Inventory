from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import EquipmentsInSurvey, Accessory

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
        
        # Show only accessories that are not assigned to any equipment and are in store
        self.fields['accessory'] = forms.ModelChoiceField(
            queryset=Accessory.objects.filter(equipment=None, return_status="Returned"),
            empty_label="Select Accessory",
            widget=forms.Select(attrs={
                'class': 'form-select',
            })
        )
        
        # Custom label to show name and serial number
        def label_from_instance(obj):
            if obj.serial_number:
                return f"{obj.name} - SN: {obj.serial_number}"
            else:
                return f"{obj.name} - SN: Not assigned"
        
        self.fields['accessory'].label_from_instance = label_from_instance
        
        # Remove unwanted fields if present
        for field in ['equipment', 'comment', 'image', 'name', 'serial_number']:
            if field in self.fields:
                self.fields.pop(field)
        
        # Store equipment for later use in save method
        self.equipment = equipment

    class Meta:
        model = Accessory
        fields = []  # We'll handle the accessory selection manually

    def save(self, commit=True):
        # Get the selected accessory
        selected_accessory = self.cleaned_data['accessory']
        
        # Assign the accessory to the equipment
        selected_accessory.equipment = self.equipment
        selected_accessory.return_status = 'In Use'
        
        if commit:
            selected_accessory.save()
        
        return selected_accessory

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
            'base_serial', 'roover_serial', 'data_logger_serial', 
            'radio_serial', 'project', 'section', 'date_receiving_from_department'
        ]
        widgets = {
            'date_of_receiving_from_supplier': forms.DateInput(attrs={'type': 'date'}),
            'date_receiving_from_department': forms.DateInput(attrs={'type': 'date'}),
        }

class AccessoryEditForm(forms.ModelForm):
    class Meta:
        model = Accessory
        fields = ['status', 'comment', 'image']
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

                # Add image upload field
                self.fields[f'accessory_{accessory.id}_image'] = forms.ImageField(
                    required=False,
                    widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
                    label='Upload Image'
                )
                
                # Store accessory ID for easy access in template
                self.fields[f'accessory_{accessory.id}'].accessory_id = accessory.id

class addEquipmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'chief_surveyor' in self.fields:
            self.fields['chief_surveyor'].queryset = User.objects.filter(is_superuser=False)
    class Meta:
        model = EquipmentsInSurvey
        fields = [
            'name',
            'owner',
            'date_of_receiving_from_supplier',
            'supplier',
            'base_serial',
            'roover_serial',
            'condition',
            'data_logger_serial',
            'radio_serial',
            'date_receiving_from_department',
        ]
        widgets = {
            'date_of_receiving_from_supplier': forms.DateInput(attrs={'type': 'date'}),
            'date_receiving_from_department': forms.DateInput(attrs={'type': 'date'}),
        }
