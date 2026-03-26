from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.messages import get_messages
from .models import Property
import os

User = get_user_model()

class LeaseProViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.u_pass = "SecureTestPass123!" 

        # Create Landlord
        self.landlord = User.objects.create_user(
            username='landlord_user', password=self.u_pass, is_landlord=True
        )
        # Create Tenant
        self.tenant = User.objects.create_user(
            username='tenant_user', password=self.u_pass, is_tenant=True
        )
        # Create Staff (to cover is_staff branches)
        self.staff = User.objects.create_user(
            username='staff_user', password=self.u_pass, is_staff=True
        )
        # Create Sample Property
        self.property = Property.objects.create(
            address="123 NCI Street",
            landlord=self.landlord,
            rent_amount=1200.00,
            description="Test description"
        )

    # --- Home & Access Tests ---
    def test_home_view(self):
        # Anonymous
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        # Authenticated (Covers the redirect branch)
        self.client.login(username='landlord_user', password=self.u_pass)
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('login_success'))

    def test_access_denied_view(self):
        response = self.client.get(reverse('access_denied'))
        self.assertEqual(response.status_code, 200)

    # --- Authentication & Signup Tests ---
    def test_signup_view(self):
        # GET
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        # Authenticated redirect
        self.client.login(username='tenant_user', password=self.u_pass)
        response = self.client.get(reverse('signup'))
        self.assertRedirects(response, reverse('login_success'))
        self.client.logout()
        # Valid POST
        data = {'username': 'newuser', 'password1': self.u_pass, 'password2': self.u_pass, 'role': 'tenant'}
        response = self.client.post(reverse('signup'), data)
        self.assertRedirects(response, reverse('login'))
        # Invalid POST (Covers the print(form.errors) branch)
        response = self.client.post(reverse('signup'), {'username': ''})
        self.assertEqual(response.status_code, 200)

    def test_login_success_logic(self):
        # Landlord
        self.client.login(username='landlord_user', password=self.u_pass)
        response = self.client.get(reverse('login_success'))
        self.assertRedirects(response, reverse('dashboard'))
        # Tenant
        self.client.login(username='tenant_user', password=self.u_pass)
        response = self.client.get(reverse('login_success'))
        self.assertRedirects(response, reverse('tenant_dashboard'))
        # Staff/Other (Covers the final 'return redirect(home)' branch)
        self.client.login(username='staff_user', password=self.u_pass)
        # Note: In your view, staff without landlord/tenant flags will hit the final home redirect
        response = self.client.get(reverse('login_success'))
        self.assertRedirects(response, reverse('home'))

    # --- Landlord Dashboard & Property Tests ---
    def test_landlord_dashboard(self):
        # Access denied for tenant
        self.client.login(username='tenant_user', password=self.u_pass)
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('access_denied'))
        # Access allowed for staff
        self.client.login(username='staff_user', password=self.u_pass)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_add_property(self):
        self.client.login(username='landlord_user', password=self.u_pass)
        # Valid
        data = {'address': 'Add Test', 'rent_amount': 500, 'description': 'New'}
        response = self.client.post(reverse('add_property'), data)
        self.assertRedirects(response, reverse('dashboard'))
        # Invalid (Covers the print(form.errors) branch)
        response = self.client.post(reverse('add_property'), {'address': ''})
        self.assertEqual(response.status_code, 200)

    def test_edit_property(self):
        url = reverse('edit_property', args=[self.property.pk])
        # Unauthorized access
        self.client.login(username='tenant_user', password=self.u_pass)
        response = self.client.get(url)
        self.assertRedirects(response, reverse('access_denied'))
        # Staff access (covers the 'or request.user.is_staff' branch)
        self.client.login(username='staff_user', password=self.u_pass)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Valid Edit
        self.client.login(username='landlord_user', password=self.u_pass)
        data = {'address': 'Updated', 'rent_amount': 2000, 'description': 'Updated'}
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('property_detail', args=[self.property.pk]))

    def test_delete_property(self):
        url = reverse('delete_property', args=[self.property.pk])
        # Unauthorized
        self.client.login(username='tenant_user', password=self.u_pass)
        response = self.client.post(url)
        self.assertRedirects(response, reverse('access_denied'))
        # Staff Delete
        self.client.login(username='staff_user', password=self.u_pass)
        response = self.client.get(url) # Covers GET confirmation page
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url) # Covers POST delete
        self.assertRedirects(response, reverse('dashboard'))

    # --- Tenant Views ---
    def test_tenant_views(self):
        self.client.login(username='tenant_user', password=self.u_pass)
        self.assertEqual(self.client.get(reverse('tenant_dashboard')).status_code, 200)
        self.assertEqual(self.client.get(reverse('tenant_browse')).status_code, 200)
        self.assertEqual(self.client.get(reverse('property_detail', args=[self.property.pk])).status_code, 200)

# --- Settings & Configuration Coverage ---
class SettingsTest(TestCase):
    def test_settings_coverage(self):
        self.assertEqual(settings.DEFAULT_AUTO_FIELD, 'django.db.models.BigAutoField')
        self.assertIn('core', settings.INSTALLED_APPS)
        self.assertTrue(os.path.exists(settings.BASE_DIR))