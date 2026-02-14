from django.contrib import admin
from .models import Property, User

# Customizing the Admin Interface Branding
admin.site.site_header = "LeasePro Administrative Portal"
admin.site.site_title = "LeasePro Admin"
admin.site.index_title = "Welcome to the LeasePro Management System"

admin.site.register(Property)
admin.site.register(User)