from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # --- Public Access & Auth ---
    # The 'home' name is the target for your 'Return to Safety' button
    path('', views.home, name='home'),
    
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('signup/', views.signup, name='signup'),

    # --- Role-Based Redirection ---
    # This view acts as the 'traffic controller' to prevent infinite loops
    path('login-success/', views.login_success, name='login_success'),

    # --- Landlord / Admin Portfolio Management ---
    # 'dashboard' is the primary redirect target for Landlord accounts
    path('dashboard/', views.landlord_dashboard, name='dashboard'),
    path('add-property/', views.add_property, name='add_property'),
    path('property/edit/<int:pk>/', views.edit_property, name='edit_property'),
    path('delete-property/<int:pk>/', views.delete_property, name='delete_property'),

    # --- Tenant Discovery & Dashboard ---
    path('tenant-dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    path('browse/', views.tenant_browse, name='tenant_browse'),
    path('property/<int:pk>/', views.property_detail, name='property_detail'),
    
    # --- Security Intercepts ---
    # Centralized access denied route for unauthorized navigation attempts
    path('access-denied/', views.access_denied, name='access_denied'),
]
if True: # Always serve media during your demo
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)