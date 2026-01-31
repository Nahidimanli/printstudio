from rest_framework import serializers
from .models import StudioProfile, Service

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ('studio', 'created_at', 'updated_at')

class StudioProfileSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = StudioProfile
        fields = (
            'id', 'user', 'username', 'email', 'business_name', 'description', 
            'address', 'latitude', 'longitude', 'services', 'created_at'
        )
        read_only_fields = ('user', 'created_at')
