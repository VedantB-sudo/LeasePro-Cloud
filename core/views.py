from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Property
from .forms import PropertyForm, LeaseProSignupForm

def home(request):
    if request.user.is_authenticated:
        return redirect('login_success')
    return render(request, 'core/home.html')

def signup(request):
    if request.method == 'POST':
        form = LeaseProSignupForm(request.POST)
        if form.is_valid():
            user = form.save() 
            messages.success(request, f'Account created for {user.username}!')
            return redirect('login')
        else:
            print(f"Form Errors: {form.errors}")
    else:
        form = LeaseProSignupForm()
    return render(request, 'core/signup.html', {'form': form})

# --- NEW: This fixes the 500 error by providing the missing view ---
def access_denied(request):
    return render(request, 'core/access_denied.html')

@login_required
def login_success(request):
    """
    Redirects users to their specific dashboard based on their role.
    Assumes your User model has 'is_landlord' and 'is_tenant' attributes.
    """
    if request.user.is_landlord:
        return redirect('dashboard')
    elif request.user.is_tenant:
        return redirect('tenant_dashboard')
    return redirect('home')

@login_required
def landlord_dashboard(request):
    # Security Intercept: Redirect tenants or non-landlords
    if not request.user.is_landlord:
        return redirect('access_denied')

    my_properties = Property.objects.filter(landlord=request.user)
    return render(request, 'core/dashboard.html', {'properties': my_properties})

@login_required
def add_property(request):
    if not request.user.is_landlord:
        return redirect('access_denied')

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES) 
        if form.is_valid():
            property_item = form.save(commit=False)
            property_item.landlord = request.user
            property_item.save()
            messages.success(request, 'Property listed successfully!')
            return redirect('dashboard')
    else:
        form = PropertyForm()
    return render(request, 'core/add_property.html', {'form': form})

@login_required
def edit_property(request, pk):
    property_instance = get_object_or_404(Property, pk=pk)
    
    # Security: Ensure only the owner can edit
    if property_instance.landlord != request.user:
        return redirect('access_denied')

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Property updated successfully.')
            return redirect('property_detail', pk=property_instance.pk)
    else:
        form = PropertyForm(instance=property_instance)
    
    return render(request, 'core/edit_property.html', {
        'form': form, 
        'property': property_instance
    })

@login_required
def delete_property(request, pk):
    property_to_delete = get_object_or_404(Property, pk=pk)

    if property_to_delete.landlord != request.user:
        return redirect('access_denied')

    if request.method == 'POST':
        property_to_delete.delete()
        messages.success(request, 'Property deleted successfully.')
        return redirect('dashboard')

    return render(request, 'core/confirm_delete.html', {'property': property_to_delete})

@login_required
def tenant_dashboard(request):
    # Displays all listings to the tenant
    properties = Property.objects.all() 
    return render(request, 'core/tenant_dashboard.html', {'properties': properties})

@login_required
def tenant_browse(request):
    all_properties = Property.objects.all()
    return render(request, 'core/tenant_browse.html', {'properties': all_properties})

@login_required
def property_detail(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    return render(request, 'core/property_detail.html', {'property': property_obj})