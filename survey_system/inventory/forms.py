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
                label=f"Quantity for {label}", 
                min_value=0, 
                initial=0, 
                required=False,
                widget=forms.NumberInput(attrs={'class': 'form-control'})
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
            'name': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'date_of_receiving_from_supplier': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
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


class CSVUploadForm(forms.Form):
    """Form for uploading CSV files to bulk add equipment"""
    csv_file = forms.FileField(
        label="CSV File",
        help_text="Upload a CSV file with equipment data. Required columns: Instrument Name, Manufacturer/Model, Serial Number(s), Condition",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv',
            'required': True
        })
    )
    
    def clean_csv_file(self):
        import csv
        import io
        
        csv_file = self.cleaned_data['csv_file']
        
        # Check file extension
        if not csv_file.name.endswith('.csv'):
            raise forms.ValidationError('File must be a CSV file.')
        
        # Check file size (limit to 5MB)
        if csv_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError('File size must be less than 5MB.')
        
        # Validate CSV format
        try:
            # Read the file content for validation
            csv_file.seek(0)  # Reset file pointer
            file_content = csv_file.read().decode('utf-8')
            csv_file.seek(0)  # Reset file pointer for later use
            
            # Parse CSV to check format
            csv_reader = csv.reader(io.StringIO(file_content))
            
            # Check if file has content
            try:
                header = next(csv_reader)
            except StopIteration:
                raise forms.ValidationError('CSV file is empty.')
            
            # Validate header has exactly 4 columns
            expected_headers = ['Instrument Name', 'Manufacturer/Model', 'Serial Number(s)', 'Condition']
            if len(header) != 4:
                raise forms.ValidationError(f'CSV must have exactly 4 columns. Found {len(header)} columns. Expected: {", ".join(expected_headers)}')
            
            # Check if headers match expected format
            header_lower = [h.strip().lower() for h in header]
            expected_lower = [h.lower() for h in expected_headers]
            if header_lower != expected_lower:
                raise forms.ValidationError(f'CSV headers must match exactly: {", ".join(expected_headers)}')
            
            # Check if there's at least one data row
            try:
                first_row = next(csv_reader)
                if len(first_row) != 4:
                    raise forms.ValidationError(f'All rows must have exactly 4 columns. First data row has {len(first_row)} columns.')
                
                # Validate first row data
                instrument_name, manufacturer, serial, condition = first_row
                
                # Check if instrument name is valid (should be in EQUIPMENT_CHOICES)
                valid_equipment = [choice[0] for choice in EquipmentsInSurvey.EQUIPMENT_CHOICES]
                if instrument_name.strip() not in valid_equipment:
                    raise forms.ValidationError(f'Invalid equipment type: "{instrument_name}". Valid options: {", ".join(valid_equipment)}')
                
                # Manufacturer validation removed - now accepts any manufacturer/model from CSV
                
                # Condition validation removed - now accepts any condition from CSV
                
                # Check if serial number is not empty
                if not serial.strip():
                    raise forms.ValidationError('Serial number cannot be empty.')
                    
            except StopIteration:
                raise forms.ValidationError('CSV file must contain at least one data row.')
                
        except UnicodeDecodeError:
            raise forms.ValidationError('File must be a valid UTF-8 encoded CSV file.')
        except Exception as e:
            raise forms.ValidationError(f'Invalid CSV file format: {str(e)}')
        
        return csv_file