from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Property

# Form for Landlords to list properties
class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['address', 'rent_amount', 'description', 'image']
        widgets = {'description': forms.Textarea(attrs={'rows': 4}),}

# Registration Form
class LeaseProSignupForm(UserCreationForm):
    ROLE_CHOICES = [
        ('landlord', 'Landlord'),
        ('tenant', 'Tenant'),
    ]
    
    # Ensure this is indented exactly 4 spaces (1 tab)
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        widget=forms.RadioSelect, 
        label="I am a:"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        # Ensure this matches the name of your ChoiceField!
        selected_role = self.cleaned_data.get('role') 
        
        if selected_role == 'landlord':
            user.is_landlord = True
            user.is_tenant = False
        else:
            user.is_landlord = False
            user.is_tenant = True
            
        if commit:
            user.save()
        return user