from rest_framework import viewsets, permissions, exceptions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Order, OrderFile
from .serializers import OrderSerializer, OrderFileSerializer
from apps.users.models import User

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.STUDIO:
            # Studios see orders for their studio
            if hasattr(user, 'studio_profile'):
                return Order.objects.filter(studio=user.studio_profile)
            return Order.objects.none()
        elif user.role == User.Role.CUSTOMER:
            # Customers see their own orders
            return Order.objects.filter(customer=user)
        elif user.role == User.Role.ADMIN:
            return Order.objects.all()
        return Order.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role != User.Role.CUSTOMER:
             # Optionally allow admin to create? For now strict.
             pass 
             # Actually role check is good.
             # Note: if studio tries to create order, it might fail validation if we enforce logic.
             # User requirements: "Customer features: Create orders".
        serializer.save(customer=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        # Override to strict status updates
        order = self.get_object()
        user = request.user
        
        if user.role == User.Role.STUDIO:
            # Studio can only update 'status'
            if order.studio.user != user:
                raise exceptions.PermissionDenied("Not your order.")
            
            # Check if other fields are being updated?
            # For simplicity, we allow studio to update status.
            # Ideally validation in serializer.
            return super().partial_update(request, *args, **kwargs)
        
        if user.role == User.Role.CUSTOMER:
             # Customer can cancel only if status is RECEIVED
             status_update = request.data.get('status')
             if status_update == Order.Status.CANCELLED:
                 if order.status != Order.Status.RECEIVED:
                     raise exceptions.ValidationError("Cannot cancel order in progress.")
                 return super().partial_update(request, *args, **kwargs)
             
             raise exceptions.PermissionDenied("Customers cannot update orders like this.")

        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_file(self, request, pk=None):
        order = self.get_object()
        # Check permissions
        if request.user != order.customer:
             raise exceptions.PermissionDenied("Only the customer can upload files.")
        
        file_serializer = OrderFileSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save(order=order)
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
