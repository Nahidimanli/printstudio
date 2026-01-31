from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from apps.studios.models import StudioProfile, Service

User = get_user_model()

class Order(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "RECEIVED", _("Order Received")
        PREPARATION = "PREPARATION", _("In Preparation")
        READY = "READY", _("Ready")
        PICKUP = "PICKUP", _("Pick up from center")
        CANCELLED = "CANCELLED", _("Cancelled")
        COMPLETED = "COMPLETED", _("Completed")

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    studio = models.ForeignKey(StudioProfile, on_delete=models.CASCADE, related_name='orders')
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RECEIVED
    )
    total_price = models.DecimalField(_("Total Price"), max_digits=12, decimal_places=2, default=0.00)
    note = models.TextField(_("Customer Note"), blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(_("Price at Order"), max_digits=10, decimal_places=2) # Snapshot of price
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.service.name if self.service else 'Unknown Service'} (x{self.quantity})"

class OrderFile(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='order_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for Order #{self.order.id}"
