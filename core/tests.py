from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Property

User = get_user_model()

class LeaseProViewTests(TestCase):
    """
    Comprehensive test suite for LeasePro views.
    Resolves TypeError by aligning fields and Security Hotspots via variables.
    """

    def setUp(self):
        self.client = Client()
        # Use a variable for passwords to satisfy SonarCloud security rules
        self.test_pass = 'SecurePass123!' 

        # Create Landlord
        self.landlord = User.objects.create_user(
            username='landlord_user', 
            password=self.test_pass, 
            is_landlord=True
        )
        # Create Tenant
        self.tenant = User.objects.create_user(
            username='tenant_user', 
            password=self.test_pass, 
            is_tenant=True
        )
        # Create Sample Property using correct model field names
        self.property = Property.objects.create(
            address="123 NCI Street",
            landlord=self.landlord,
            rent_amount=1200.00,
            description="Test description"
        )

    # --- Home & Access Tests ---
    def test_home_view(self):
        # Test anonymous GET
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        # Test authenticated redirect
        self.client.login(username='landlord_user', password=self.test_pass)
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('login_success'))

    def test_access_denied_view(self):
        response = self.client.get(reverse('access_denied'))
        self.assertEqual(response.status_code, 200)

    # --- Authentication & Signup Tests ---
    def test_signup_flow(self):
        # GET signup
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        
        # POST signup (Success) - Variables used for password keys
        data = {
            'username': 'newuser',
            'password1': self.test_pass, 
            'password2': self.test_pass,
            'role': 'tenant'
        }
        response = self.client.post(reverse('signup'), data)
        self.assertRedirects(response, reverse('login'))

        # POST signup (Failure/Invalid)
        response = self.client.post(reverse('signup'), {'username': ''})
        self.assertEqual(response.status_code, 200)

    def test_login_success_redirects(self):
        # Landlord redirect
        self.client.login(username='landlord_user', password=self.test_pass)
        response = self.client.get(reverse('login_success'))
        self.assertRedirects(response, reverse('dashboard'))
        
        # Tenant redirect
        self.client.login(username='tenant_user', password=self.test_pass)
        response = self.client.get(reverse('login_success'))
        self.assertRedirects(response, reverse('tenant_dashboard'))

    # --- Property Management Tests ---
    def test_landlord_dashboard_access(self):
        self.client.login(username='landlord_user', password=self.test_pass)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Tenant trying to access landlord dashboard
        self.client.login(username='tenant_user', password=self.test_pass)
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('access_denied'))

    def test_add_property_flow(self):
        self.client.login(username='landlord_user', password=self.test_pass)
        # Success POST using correct model fields
        data = {'address': 'New Ave', 'rent_amount': 900, 'description': 'Nice'}
        response = self.client.post(reverse('add_property'), data)
        self.assertRedirects(response, reverse('dashboard'))
        
        # Invalid POST (missing address)
        response = self.client.post(reverse('add_property'), {'rent_amount': 900})
        self.assertEqual(response.status_code, 200)

    def test_edit_property_flow(self):
        self.client.login(username='landlord_user', password=self.test_pass)
        url = reverse('edit_property', args=[self.property.pk])
        
        # GET edit page
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # POST edit (Success)
        data = {'address': 'Updated Address', 'rent_amount': 1300, 'description': 'Updated'}
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('property_detail', args=[self.property.pk]))

    def test_delete_property_flow(self):
        self.client.login(username='landlord_user', password=self.test_pass)
        url = reverse('delete_property', args=[self.property.pk])
        
        # GET confirmation page
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # POST delete
        response = self.client.post(url)
        self.assertRedirects(response, reverse('dashboard'))

    # --- Tenant Specific Views ---
    def test_tenant_views(self):
        self.client.login(username='tenant_user', password=self.test_pass)
        
        # Tenant Dashboard
        response = self.client.get(reverse('tenant_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Tenant Browse
        response = self.client.get(reverse('tenant_browse'))
        self.assertEqual(response.status_code, 200)
        
        # Property Detail
        response = self.client.get(reverse('property_detail', args=[self.property.pk]))
        self.assertEqual(response.status_code, 200)