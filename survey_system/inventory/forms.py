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

    class Meta:
        model = Accessory
        fields = '__all__'
        widgets = {
            'name': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Select Accessory Type'
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
