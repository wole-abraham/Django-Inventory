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
            serial_number=self.equipment.base_serial if self.equipment else None,
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
            'base_serial', 'roover_serial', 'project', 'section', 'date_receiving_from_department'
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
            'base_serial',
            'roover_serial',
            'condition',
        ]
        widgets = {
            'date_of_receiving_from_supplier': forms.DateInput(attrs={'type': 'date'}),
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

