import os

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

class User(AbstractUser):
    """
    Custom User model for LeasePro.
    Supports role-based access for Landlords and Tenants.
    """
    is_landlord = models.BooleanField(default=False)
    is_tenant = models.BooleanField(default=False)

class Property(models.Model):
    """
    Represents a rental property listing.
    Includes landlord assignment, pricing, and media storage.
    """
    landlord = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='properties'
    )
    address = models.CharField(max_length=255)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='property_images/', null=True, blank=True)
    objects = models.Manager()

    class Meta:
        """
        Metadata for the Property model.
        """
        verbose_name = "Property"
        verbose_name_plural = "Properties"

    def __str__(self):
        """
        Returns the property address as its string representation.
        """
        return str(self.address)

@receiver(post_delete, sender=Property)
def auto_delete_file_on_delete(_sender, instance, **kwargs):
    """
    Deletes image file from filesystem when corresponding Property object is deleted.
    
    Pylint Fix: Renamed 'sender' to '_sender' to resolve W0613 (unused-argument).
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)