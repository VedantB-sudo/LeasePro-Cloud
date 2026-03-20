from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Auth Views: Standardized to 'core/' folder to match your project structure
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('signup/', views.signup, name='signup'),

    # --- Role-Based Logic ---
    # This 'Smart' Redirect ensures Landlords and Tenants go to the right places
    path('login-success/', views.login_success, name='login_success'),

    # --- Landlord Dashboard & Management (Secure CRUD) ---
    path('dashboard/', views.landlord_dashboard, name='dashboard'),
    path('add-property/', views.add_property, name='add_property'),
    path('property/edit/<int:pk>/', views.edit_property, name='edit_property'),
    path('delete-property/<int:pk>/', views.delete_property, name='delete_property'),

    # --- Tenant & Public Discovery (Non-CRUD) ---
    path('browse/', views.tenant_browse, name='tenant_browse'),
    path('tenant-dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    path('property/<int:pk>/', views.property_detail, name='property_detail'),
    
    # --- Security & Error Intercepts ---
    # Explicitly mapping the access denied view for better logging
    path('access-denied/', views.access_denied, name='access_denied'),
]