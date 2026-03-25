from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_GET

from .models import Property
from .forms import PropertyForm, LeaseProSignupForm

@require_GET
def home(request):
    """
    Home page view. 
    Only redirects to login_success if the user is authenticated 
    to avoid the infinite loop for users without roles.
    """
    if request.user.is_authenticated:
        return redirect('login_success')
    return render(request, 'core/home.html')

def signup(request):
    if request.user.is_authenticated:
        return redirect('login_success')
        
    if request.method == 'POST':
        form = LeaseProSignupForm(request.POST)
        if form.is_valid():
            user = form.save() 
            messages.success(request, f'Account created for {user.username}!')
            return redirect('login')
        
        # Pylint R1705 Fix: Removed 'else' after 'return'
        # Code execution only reaches here if form.is_valid() is False
        print(f"Form Errors: {form.errors}")
    
    # Pylint R1705 Fix: Removed 'else' after 'if request.method == POST'
    # Code execution reaches here for GET requests or failed POST submissions
    form = LeaseProSignupForm()
    return render(request, 'core/signup.html', {'form': form})

@require_GET
def access_denied(request):
    """
    Renders the custom access denied template.
    SonarQube Fix: Restricted to safe GET method only.
    """
    return render(request, 'core/access_denied.html')

@login_required
@require_GET
def login_success(request):
    """
    Role-based redirector. 
    Fixes the 'Too Many Redirects' loop by ensuring every user type 
    has a concrete destination.
    """
    if request.user.is_landlord:
        return redirect('dashboard')
    elif request.user.is_tenant:
        return redirect('tenant_dashboard')
    
    # SAFE FALLBACK: If user is an Admin/Superuser or role-less, 
    # send them to the primary dashboard to break the loop.
    return redirect('dashboard')

@login_required
@require_GET
def landlord_dashboard(request):
    """
    SonarQube Fix: Added @require_GET as this view only fetches data.
    """
    # Security Intercept: Redirect tenants or unauthorized users to safety
    if not request.user.is_landlord and not request.user.is_staff:
        return redirect('access_denied')

    my_properties = Property.objects.filter(landlord=request.user)
    return render(request, 'core/dashboard.html', {'properties': my_properties})

@login_required
def add_property(request):
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
    else:
        form = PropertyForm()
    return render(request, 'core/add_property.html', {'form': form})

@login_required
def edit_property(request, pk):
    property_instance = get_object_or_404(Property, pk=pk)
    
    # Security: Ensure only the owner (or staff) can edit
    if property_instance.landlord != request.user and not request.user.is_staff:
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
    SonarQube Fix: Added @require_GET.
    """
    # Displays all listings to the tenant
    properties = Property.objects.all() 
    return render(request, 'core/tenant_dashboard.html', {'properties': properties})

@login_required
@require_GET
def tenant_browse(request):
    """
    SonarQube Fix: Added @require_GET.
    """
    all_properties = Property.objects.all()
    return render(request, 'core/tenant_browse.html', {'properties': all_properties})

@login_required
@require_GET
def property_detail(request, pk):
    """
    SonarQube Fix: Added @require_GET.
    """
    property_obj = get_object_or_404(Property, pk=pk)
    return render(request, 'core/property_detail.html', {'property': property_obj})