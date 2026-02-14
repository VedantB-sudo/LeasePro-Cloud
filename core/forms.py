from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Property

# Form for Landlords to list properties
class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['address', 'rent_amount', 'description', 'image']
        widgets = {'description': forms.Textarea(attrs={'rows': 4}),}

# This is the class your views.py is looking for
class LeaseProSignupForm(UserCreationForm):
    ROLE_CHOICES = [
        ('landlord', 'Landlord'),
        ('tenant', 'Tenant'),
    ]
    
    # Custom role selection field
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        widget=forms.RadioSelect, 
        label="I am a:"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # We define exactly which fields should appear in the form
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')
        
        # Mapping the radio button choice to your model Boolean fields
        if role == 'landlord':
            user.is_landlord = True
            user.is_tenant = False
        elif role == 'tenant':
            user.is_landlord = False
            user.is_tenant = True
            
        if commit:
            user.save()
        return user