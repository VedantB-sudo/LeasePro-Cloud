"""
Views for the LeasePro application.
Handles user authentication, property management, and role-based dashboards.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from .models import Property
from .forms import PropertyForm, LeaseProSignupForm

@require_GET
def home(request):
    """
    Renders the home page. Redirects authenticated users to avoid loops.
    """
    if request.user.is_authenticated:
        return redirect('login_success')
    return render(request, 'core/home.html')

@require_http_methods(["GET", "POST"])
def signup(request):
    """
    Handles user registration. 
    SonarQube Fix: Restricted to specific methods to resolve security hotspot.
    """
    if request.user.is_authenticated:
        return redirect('login_success')
        
    if request.method == 'POST':
        form = LeaseProSignupForm(request.POST)
        if form.is_valid():
            user = form.save() 
            messages.success(request, f'Account created for {user.username}!')
            return redirect('login')
        
        # Pylint R1705 Fix: Removed 'else' after 'return'
        print(f"Form Errors: {form.errors}")
    
    # Execution reaches here for GET requests or failed POST submissions
    form = LeaseProSignupForm()
    return render(request, 'core/signup.html', {'form': form})

@require_GET
def access_denied(request):
    """
    Renders the custom access denied template.
    """
    return render(request, 'core/access_denied.html')

@login_required
@require_GET
def login_success(request):
    """
    Redirects users to their respective dashboards based on roles.
    """
    if request.user.is_landlord:
        return redirect('dashboard')
    
    if request.user.is_tenant:
        return redirect('tenant_dashboard')
    
    # Pylint R1705 Fix: Removed elif/else after return
    return redirect('dashboard')

@login_required
@require_GET
def landlord_dashboard(request):
    """
    Displays properties belonging to the logged-in landlord.
    """
    if not request.user.is_landlord and not request.user.is_staff:
        return redirect('access_denied')

    my_properties = Property.objects.filter(landlord=request.user)
    return render(request, 'core/dashboard.html', {'properties': my_properties})

@login_required
@require_http_methods(["GET", "POST"])
def add_property(request):
    """
    Allows landlords to add new property listings.
    """
    if not request.user.is_landlord and not request.user.is_staff:
        return redirect('access_denied')

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES) 
        if form.is_valid():
            property_item = form.save(commit=False)
            property_item.landlord = request.user
            property_item.save()
            messages.success(request, 'Property listed successfully!')
            return redirect('dashboard')
            
    # Pylint R1705 Fix: Logic flattened
    form = PropertyForm()
    return render(request, 'core/add_property.html', {'form': form})

@login_required
@require_http_methods(["GET", "POST"])
def edit_property(request, pk):
    """
    Allows landlords to update existing property details.
    """
    property_instance = get_object_or_404(Property, pk=pk)
    
    if property_instance.landlord != request.user and not request.user.is_staff:
        return redirect('access_denied')

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Property updated successfully.')
            return redirect('property_detail', pk=property_instance.pk)
    
    # Pylint R1705 Fix: Logic flattened
    form = PropertyForm(instance=property_instance)
    return render(request, 'core/edit_property.html', {
        'form': form, 
        'property': property_instance
    })

@login_required
@require_http_methods(["GET", "POST"])
def delete_property(request, pk):
    """
    Handles property deletion after confirmation.
    """
    property_to_delete = get_object_or_404(Property, pk=pk)

    if property_to_delete.landlord != request.user and not request.user.is_staff:
        return redirect('access_denied')

    if request.method == 'POST':
        property_to_delete.delete()
        messages.success(request, 'Property deleted successfully.')
        return redirect('dashboard')

    return render(request, 'core/confirm_delete.html', {'property': property_to_delete})

@login_required
@require_GET
def tenant_dashboard(request):
    """
    Displays all available listings to tenants.
    """
    properties = Property.objects.all() 
    return render(request, 'core/tenant_dashboard.html', {'properties': properties})

@login_required
@require_GET
def tenant_browse(request):
    """
    Dedicated view for browsing all properties.
    """
    all_properties = Property.objects.all()
    return render(request, 'core/tenant_browse.html', {'properties': all_properties})

@login_required
@require_GET
def property_detail(request, pk):
    """
    Displays full details for a single property.
    """
    property_obj = get_object_or_404(Property, pk=pk)
    return render(request, 'core/property_detail.html', {'property': property_obj})