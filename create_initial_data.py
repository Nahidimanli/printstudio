import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from apps.studios.models import StudioProfile, Service

User = get_user_model()

def create_data():
    # Superuser
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@example.com", "admin", role=User.Role.ADMIN)
        print("Superuser 'admin' created.")
    
    # Studio User
    studio_user, created = User.objects.get_or_create(
        username="studio", 
        defaults={
            "email": "studio@example.com",
            "role": User.Role.STUDIO,
            "is_active": True
        }
    )
    if created:
        studio_user.set_password("studio123")
        studio_user.save()
        print("Studio user 'studio' created.")

    # Studio Profile
    if not hasattr(studio_user, 'studio_profile'):
        profile = StudioProfile.objects.create(
            user=studio_user,
            business_name="Elite Photography",
            description="Professional photography services.",
            address="123 Main St, Tech City",
            latitude=40.7128,
            longitude=-74.0060
        )
        print("Studio Profile created.")
        
        # Service
        Service.objects.create(
            studio=profile,
            name="Wedding Photoshoot",
            description="Full day coverage",
            price=1500.00,
            duration_minutes=480
        )
        print("Service 'Wedding Photoshoot' created.")

    # Customer User
    customer_user, created = User.objects.get_or_create(
        username="customer", 
        defaults={
            "email": "customer@example.com",
            "role": User.Role.CUSTOMER,
            "is_active": True
        }
    )
    if created:
        customer_user.set_password("customer123")
        customer_user.save()
        print("Customer user 'customer' created.")

if __name__ == "__main__":
    create_data()
