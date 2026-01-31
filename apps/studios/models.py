from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class StudioProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='studio_profile')
    business_name = models.CharField(_("Business Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    address = models.TextField(_("Address"), blank=True)
    latitude = models.FloatField(_("Latitude"), null=True, blank=True)
    longitude = models.FloatField(_("Longitude"), null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name or self.user.username

class Service(models.Model):
    studio = models.ForeignKey(StudioProfile, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(_("Service Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(_("Duration (Minutes)"), default=60, help_text="Estimated duration")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.studio.business_name}"
