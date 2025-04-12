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
        
        if equipment:
            self.fields['equipment'].initial = equipment
            self.fields['equipment'].disabled = True
            self.fields['equipment'].widget.attrs['class'] = 'form-select'
        

        self.fields['name'] = forms.ModelChoiceField(
            queryset=Accessory.objects.filter(status='Good', return_status="Returned"),
            empty_label="Select Accessory Type",  # Optional: placeholder for dropdown
            widget=forms.Select(attrs={
                'class': 'form-select',
            })
        )

    class Meta:
        model = Accessory
        fields = ['name', 'serial_number', 'equipment', 'comment', 'image']
        widgets = {
            'name': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Select Accessory Type'
            }),
            'serial_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter serial number'
            }),
            'equipment': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Select Equipment'
            }),
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

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.return_status = 'In Use'  # Set default return status
        if commit:
            instance.save()
        return instance

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
