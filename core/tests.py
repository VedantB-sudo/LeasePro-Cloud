from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Property

User = get_user_model()

class LeaseProViewTests(TestCase):
    """
    Comprehensive test suite for LeasePro views to satisfy code coverage.
    Updated to use correct model fields: 'address' and 'rent_amount'.
    """

    def setUp(self):
        self.client = Client()
        # Create a Landlord user
        self.landlord = User.objects.create_user(
            username='landlord_user', 
            password='password123', 
            is_landlord=True
        )
        # Create a Tenant user
        self.tenant = User.objects.create_user(
            username='tenant_user', 
            password='password123', 
            is_tenant=True
        )
        # Create a sample Property using correct field names
        self.property = Property.objects.create(
            address="Dublin Apartment",
            landlord=self.landlord,
            rent_amount=1500.00,
            description="A lovely city center apartment."
        )

    # --- Home & Auth Tests ---
    def test_home_view_anonymous(self):
        """Verify home page loads for unauthenticated users."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_view_authenticated_redirect(self):
        """Verify home page redirects logged-in users to prevent loops."""
        self.client.login(username='landlord_user', password='password123')
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('login_success'))

    def test_signup_get(self):
        """Verify signup page renders correctly."""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

    def test_signup_post_success(self):
        """Verify successful user registration."""
        data = {
            'username': 'new_user',
            'password1': 'StrongPassword123!', # Changed from 'password'
            'password2': 'StrongPassword123!', # Changed from 'confirm_password'
            'role': 'tenant'
        }
        response = self.client.post(reverse('signup'), data)
        self.assertRedirects(response, reverse('login'))

    def test_login_success_redirect_landlord(self):
        """Verify landlords go to the correct dashboard."""
        self.client.login(username='landlord_user', password='password123')
        response = self.client.get(reverse('login_success'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_success_redirect_tenant(self):
        """Verify tenants go to the correct dashboard."""
        self.client.login(username='tenant_user', password='password123')
        response = self.client.get(reverse('login_success'))
        self.assertRedirects(response, reverse('tenant_dashboard'))

    # --- Property Management Tests ---
    def test_add_property_get(self):
        """Verify add_property page renders for landlords."""
        self.client.login(username='landlord_user', password='password123')
        response = self.client.get(reverse('add_property'))
        self.assertEqual(response.status_code, 200)

    def test_add_property_post_success(self):
        """Verify landlords can successfully add a property."""
        self.client.login(username='landlord_user', password='password123')
        # Ensure 'address' and 'rent_amount' are used, not 'title' or 'price'
        data = {
            'address': 'Cork Cottage',
            'rent_amount': 1200.00,
            'description': 'Rural escape.'
        }
        response = self.client.post(reverse('add_property'), data)
        self.assertRedirects(response, reverse('dashboard'))

    def test_edit_property_unauthorized(self):
        """Verify tenants cannot edit a landlord's property."""
        self.client.login(username='tenant_user', password='password123')
        response = self.client.get(reverse('edit_property', args=[self.property.pk]))
        self.assertRedirects(response, reverse('access_denied'))

    def test_delete_property_post(self):
        """Verify landlords can delete their own property via POST."""
        self.client.login(username='landlord_user', password='password123')
        response = self.client.post(reverse('delete_property', args=[self.property.pk]))
        self.assertRedirects(response, reverse('dashboard'))
        self.assertFalse(Property.objects.filter(pk=self.property.pk).exists())

    # --- Public/Tenant Views ---
    def test_property_detail_view(self):
        """Verify single property view loads correctly."""
        self.client.login(username='tenant_user', password='password123')
        response = self.client.get(reverse('property_detail', args=[self.property.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dublin Apartment")

    def test_tenant_browse_view(self):
        """Verify browse listings view loads for tenants."""
        self.client.login(username='tenant_user', password='password123')
        response = self.client.get(reverse('tenant_browse'))
        self.assertEqual(response.status_code, 200)

    def test_access_denied_view(self):
        """Verify the custom access denied page renders."""
        response = self.client.get(reverse('access_denied'))
        self.assertEqual(response.status_code, 200)