from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home and Auth
    path('', views.home, name='home'),
    
    # Change 'core/login.html' to 'login.html' if your file is in the main templates folder
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('signup/', views.signup, name='signup'),

    # The "Smart" Redirect (Point your LOGIN_REDIRECT_URL to this)
    path('login-success/', views.login_success, name='login_success'),

    # Landlord Routes
    path('dashboard/', views.landlord_dashboard, name='dashboard'),
    path('add-property/', views.add_property, name='add_property'),
    path('property/edit/<int:pk>/', views.edit_property, name='edit_property'),
    path('delete-property/<int:pk>/', views.delete_property, name='delete_property'),

    # Tenant Routes
    path('browse/', views.tenant_browse, name='tenant_browse'),
    path('tenant-dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    path('property/<int:pk>/', views.property_detail, name='property_detail'),
]