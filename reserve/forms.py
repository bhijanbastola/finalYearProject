
from django import forms
from .models import Booking, Guide, Resturant, Customer, Review
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class GuideForm(forms.ModelForm):
    class Meta:
        model = Guide
        fields = ['first_name', 'last_name', 'email', 'phone', 'specialization', 'experience_years', 'is_available']

class ResturantForm(forms.ModelForm):
    class Meta:
        model = Resturant
        fields = ['name', 'destination', 'email', 'phone', 'cuisine_type', 'average_cost', 'is_open']


    class CustomerRegistrationForm(UserCreationForm):
       email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user    
    
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone']

class BookingForm(forms.ModelForm):
    guide = forms.ModelChoiceField(
        queryset=Guide.objects.filter(is_available=True),
        required=False
    )

    travel_date = forms.DateField(
        widget=forms.SelectDateWidget
    )

    class Meta:
        model = Booking
        fields = [
            'package',
            'guide',
            'hotel',
            'travel_date',
            'number_of_people'
        ]

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Review
        fields = ['rating', 'review_text']
        widgets = {
            'review_text': forms.Textarea(attrs={'rows': 4}),
        }





