from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Property
from .forms import PropertyForm, LeaseProSignupForm # Consolidated imports

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')

def signup(request):
    if request.method == 'POST':
        form = LeaseProSignupForm(request.POST)
        if form.is_valid(): 
            form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')
        else:
            # IMPORTANT: This prints the errors to your VS Code / CMD terminal
            # Check here if the password was too short or email already exists!
            print(f"Form Errors: {form.errors}") 
    else:
        form = LeaseProSignupForm()
    return render(request, 'core/signup.html', {'form': form})

@login_required
def landlord_dashboard(request):
    if request.user.is_tenant and not request.user.is_landlord:
        return redirect('tenant_browse')
    if not request.user.is_landlord:
        return render(request, 'core/access_denied.html')

    my_properties = Property.objects.filter(landlord=request.user)
    return render(request, 'core/dashboard.html', {'properties': my_properties})

@login_required
def add_property(request):
    if request.method == 'POST':
        # Notice we add request.FILES here
        form = PropertyForm(request.POST, request.FILES) 
        if form.is_valid():
            property_item = form.save(commit=False)
            property_item.landlord = request.user
            property_item.save()
            messages.success(request, 'Property listed with image successfully!')
            return redirect('dashboard')
    else:
        form = PropertyForm()
    return render(request, 'core/add_property.html', {'form': form})

@login_required
def tenant_browse(request):
    all_properties = Property.objects.all()
    return render(request, 'core/tenant_browse.html', {'properties': all_properties})

@login_required
def delete_property(request, pk):
    # Fetch the property and ensure the user owns it
    property_to_delete = get_object_or_404(Property, pk=pk)

    # Security: Secondary check to prevent unauthorized deletion
    if property_to_delete.landlord != request.user:
        return render(request, 'core/access_denied.html')

    if request.method == 'POST':
        property_to_delete.delete()
        messages.success(request, 'Property deleted successfully.')
        return redirect('dashboard') # Send landlord back to their list

    # If it's a GET request, show the confirmation page
    return render(request, 'core/confirm_delete.html', {'property': property_to_delete})

@login_required
def property_detail(request, pk):
    """
    Fetches a specific property by its ID (pk).
    """
    property = get_object_or_404(Property, pk=pk)
    return render(request, 'core/property_detail.html', {'property': property})

@login_required
def edit_property(request, pk):
    # Fetch the specific property or return 404 if not found
    property_instance = get_object_or_404(Property, pk=pk)
    
    # Security: Ensure only the owner can edit
    if property_instance.landlord != request.user and not request.user.is_staff:
        return redirect('dashboard')

    if request.method == 'POST':
        # Pass 'instance' so Django updates the existing record instead of creating a new one
        form = PropertyForm(request.POST, request.FILES, instance=property_instance)
        if form.is_valid():
            form.save()
            return redirect('property_detail', pk=property_instance.pk)
    else:
        form = PropertyForm(instance=property_instance)
    
    return render(request, 'core/edit_property.html', {
        'form': form, 
        'property': property_instance
    })

@login_required
def dashboard(request):
    properties = Property.objects.filter(landlord=request.user)
    return render(request, 'core/dashboard.html', {'properties': properties})

@login_required
def tenant_dashboard(request):
    # This view displays all listings to the tenant
    properties = Property.objects.all() 
    return render(request, 'core/tenant_dashboard.html', {'properties': properties})

@login_required
def login_success(request):
    # Check if user is in 'Landlord' group OR is a superuser (for testing)
    if request.user.groups.filter(name='Landlord').exists() or request.user.is_superuser:
        return redirect('dashboard') 
    else:
        return redirect('tenant_dashboard')