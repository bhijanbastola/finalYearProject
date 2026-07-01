# maps/forms.py
# Forms for adding Tourist Attractions and EV Charging Stations

from django import forms
from .models import TouristAttraction, EVChargingStation


class TouristAttractionForm(forms.ModelForm):
    """Form to add a new tourist attraction with image upload"""
    
    class Meta:
        model = TouristAttraction
        fields = [
            'name', 'description', 'latitude', 'longitude', 'address',
            'category', 'rating', 'entry_fee', 'opening_time', 'closing_time',
            'contact_number', 'website', 'image', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Swayambhunath Temple'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe this attraction...'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 27.7149',
                'step': 'any'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 85.2906',
                'step': 'any'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Kathmandu, Nepal'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0-5',
                'step': '0.1',
                'min': '0',
                'max': '5'
            }),
            'entry_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 200'
            }),
            'opening_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'closing_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., +977-1-1234567'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': 'Attraction Name',
            'description': 'Description',
            'latitude': 'Latitude',
            'longitude': 'Longitude',
            'address': 'Address',
            'category': 'Category',
            'rating': 'Rating (0-5)',
            'entry_fee': 'Entry Fee (NPR)',
            'opening_time': 'Opening Time',
            'closing_time': 'Closing Time',
            'contact_number': 'Contact Number',
            'website': 'Website URL',
            'image': 'Upload Image',
            'is_active': 'Active (visible on map)',
        }
    
    def clean_latitude(self):
        lat = self.cleaned_data.get('latitude')
        if lat and (lat < -90 or lat > 90):
            raise forms.ValidationError('Latitude must be between -90 and 90')
        return lat
    
    def clean_longitude(self):
        lng = self.cleaned_data.get('longitude')
        if lng and (lng < -180 or lng > 180):
            raise forms.ValidationError('Longitude must be between -180 and 180')
        return lng


class EVChargingStationForm(forms.ModelForm):
    """Form to add a new EV charging station with image upload"""
    
    class Meta:
        model = EVChargingStation
        fields = [
            'name', 'description', 'latitude', 'longitude', 'address',
            'charger_type', 'power_level', 'number_of_ports', 'charging_speed',
            'is_operational', 'cost_per_kwh', 'operator', 'available_24_7',
            'requires_membership', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Kathmandu EV Hub'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe this charging station...'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 27.7172',
                'step': 'any'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 85.3240',
                'step': 'any'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Thamel, Kathmandu'
            }),
            'charger_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'power_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'number_of_ports': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 4',
                'min': '1'
            }),
            'charging_speed': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 50 kW'
            }),
            'is_operational': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'cost_per_kwh': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 15.50',
                'step': '0.01'
            }),
            'operator': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Nepal EV Infrastructure'
            }),
            'available_24_7': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'requires_membership': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': 'Station Name',
            'description': 'Description',
            'latitude': 'Latitude',
            'longitude': 'Longitude',
            'address': 'Address',
            'charger_type': 'Charger Type',
            'power_level': 'Power Level',
            'number_of_ports': 'Number of Ports',
            'charging_speed': 'Charging Speed',
            'is_operational': 'Currently Operational',
            'cost_per_kwh': 'Cost per kWh (NPR)',
            'operator': 'Operator/Company',
            'available_24_7': 'Available 24/7',
            'requires_membership': 'Requires Membership',
            'image': 'Upload Image',
            'is_active': 'Active (visible on map)',
        }
    
    def clean_latitude(self):
        lat = self.cleaned_data.get('latitude')
        if lat and (lat < -90 or lat > 90):
            raise forms.ValidationError('Latitude must be between -90 and 90')
        return lat
    
    def clean_longitude(self):
        lng = self.cleaned_data.get('longitude')
        if lng and (lng < -180 or lng > 180):
            raise forms.ValidationError('Longitude must be between -180 and 180')
        return lng
    
    def clean_number_of_ports(self):
        ports = self.cleaned_data.get('number_of_ports')
        if ports and ports < 1:
            raise forms.ValidationError('Number of ports must be at least 1')
        return ports