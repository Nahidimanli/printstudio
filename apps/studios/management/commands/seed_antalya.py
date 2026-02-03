from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.studios.models import StudioProfile, Service
from faker import Faker
import random

User = get_user_model()
fake = Faker('tr_TR')

class Command(BaseCommand):
    help = 'Seeds database with Antalya studios'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        
        # Antalya coordinates approx range
        # Lat: 36.8 - 36.9
        # Lng: 30.6 - 30.8
        
        base_lat = 36.8841
        base_lng = 30.7056
        
        studios_data = [
            {"name": "Antalya Profesyonel Baskı", "offset": (0.01, 0.01)},
            {"name": "Konyaaltı Matbaacılık", "offset": (0.005, -0.02)},
            {"name": "Lara Dijital Baskı", "offset": (-0.01, 0.03)},
            {"name": "Muratpaşa Kartvizit", "offset": (0.002, 0.005)},
            {"name": "Akdeniz Reklam & Tabela", "offset": (-0.02, -0.01)},
            {"name": "Kaleiçi Fotoğraf Stüdyosu", "offset": (0.001, 0.001)},
            {"name": "Kepez Ofset", "offset": (0.03, -0.01)},
            {"name": "Işıklar Copy Center", "offset": (-0.005, 0.015)},
            {"name": "Meltem Grafik Tasarım", "offset": (0.008, -0.015)},
            {"name": "Uncalı Baskı Merkezi", "offset": (0.015, -0.03)},
        ]

        for i, data in enumerate(studios_data):
            username = f'studio_antalya_{i}'
            email = f'antalya{i}@example.com'
            
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, email=email, password='password123')
                user.role = User.Role.STUDIO
                user.save()
                
                lat = base_lat + data["offset"][0] + random.uniform(-0.001, 0.001)
                lng = base_lng + data["offset"][1] + random.uniform(-0.001, 0.001)
                
                studio = StudioProfile.objects.create(
                    user=user,
                    business_name=data["name"],
                    description=f"{data['name']} olarak Antalya'da hizmetinizdeyiz. Kartvizit, broşür ve her türlü baskı işleri.",
                    address=f"Antalya, Türkiye - {fake.street_address()}",
                    latitude=lat,
                    longitude=lng
                )
                
                # Create Services
                Service.objects.create(
                    studio=studio,
                    name="Standart Kartvizit (1000 Adet)",
                    price=random.choice([250, 300, 350, 400]),
                    description="Kaliteli kağıt, parlak selefon."
                )
                
                Service.objects.create(
                    studio=studio,
                    name="A5 El İlanı (5000 Adet)",
                    price=random.choice([1200, 1500, 1800]),
                    discount_price=random.choice([1000, 1300, 1600]),
                    description="Renkli baskı, kısa sürede teslim."
                )
                
                self.stdout.write(self.style.SUCCESS(f'Created studio: {data["name"]}'))
            else:
                self.stdout.write(f'Studio {data["name"]} already exists.')
        
        self.stdout.write(self.style.SUCCESS('Seeding completed!'))
