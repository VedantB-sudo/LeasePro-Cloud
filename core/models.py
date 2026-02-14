from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # These fields help you control access in your views
    is_landlord = models.BooleanField(default=False)
    is_tenant = models.BooleanField(default=False)

class Property(models.Model):
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    address = models.CharField(max_length=255)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='property_images/', null=True, blank=True)

    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"

    def __str__(self):
        return self.address
    
import os
from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=Property)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes image file from filesystem when corresponding Property object is deleted."""
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)