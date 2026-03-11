from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.landlord_dashboard, name='dashboard'),
    path('add-property/', views.add_property, name='add_property'),
    path('delete-property/<int:pk>/', views.delete_property, name='delete_property'),
    path('browse/', views.tenant_browse, name='tenant_browse'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('property/<int:pk>/', views.property_detail, name='property_detail'),
    path('property/edit/<int:pk>/', views.edit_property, name='edit_property'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login-success/', views.login_success, name='login_success'),
    path('tenant-dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
]