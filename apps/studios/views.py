from rest_framework import viewsets, permissions, filters, exceptions
from .models import StudioProfile, Service
from .serializers import StudioProfileSerializer, ServiceSerializer
from apps.users.models import User

class IsStudioOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class IsStudioOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == User.Role.STUDIO

class StudioViewSet(viewsets.ModelViewSet):
    queryset = StudioProfile.objects.all()
    serializer_class = StudioProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsStudioOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['business_name', 'description']

    def perform_create(self, serializer):
        if self.request.user.role != User.Role.STUDIO:
            raise exceptions.PermissionDenied("Only users with STUDIO role can create a studio profile.")
        if StudioProfile.objects.filter(user=self.request.user).exists():
             raise exceptions.ValidationError("Studio profile already exists for this user.")
        serializer.save(user=self.request.user)

class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = [IsStudioOrReadOnly]

    def get_queryset(self):
        # Allow filtering by studio_id in query params
        queryset = Service.objects.all()
        studio_id = self.request.query_params.get('studio_id')
        if studio_id:
            queryset = queryset.filter(studio_id=studio_id)
        return queryset

    def perform_create(self, serializer):
        # Ensure user has a studio profile
        try:
            studio = self.request.user.studio_profile
        except StudioProfile.DoesNotExist:
             raise exceptions.ValidationError("You must have a studio profile to add services.")
        serializer.save(studio=studio)

    def perform_update(self, serializer):
        # Ensure the service belongs to the user's studio
        obj = self.get_object()
        if obj.studio.user != self.request.user:
            raise exceptions.PermissionDenied("You do not own this service.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.studio.user != self.request.user:
             raise exceptions.PermissionDenied("You do not own this service.")
        instance.delete()
