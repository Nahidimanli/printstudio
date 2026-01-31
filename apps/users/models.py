from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", _("Admin")
        STUDIO = "STUDIO", _("Studio")
        CUSTOMER = "CUSTOMER", _("Customer")
        UNASSIGNED = "UNASSIGNED", _("Unassigned")

    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        default=Role.CUSTOMER,
        verbose_name=_("Role")
    )

    def __str__(self):
        return self.username
