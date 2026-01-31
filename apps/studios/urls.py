from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudioViewSet, ServiceViewSet

router = DefaultRouter()
router.register(r'studios', StudioViewSet, basename='studio')
router.register(r'services', ServiceViewSet, basename='service')

urlpatterns = [
    path('', include(router.urls)),
]
