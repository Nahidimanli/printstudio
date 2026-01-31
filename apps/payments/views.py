from rest_framework import viewsets, permissions, status, exceptions
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer
from apps.users.models import User
from apps.orders.models import Order
import uuid

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.STUDIO:
            return Payment.objects.filter(order__studio__user=user)
        elif user.role == User.Role.CUSTOMER:
            return Payment.objects.filter(order__customer=user)
        elif user.role == User.Role.ADMIN:
            return Payment.objects.all()
        return Payment.objects.none()

    def perform_create(self, serializer):
        # Validate order ownership
        order = serializer.validated_data['order']
        if order.customer != self.request.user:
             raise exceptions.PermissionDenied("Not your order.")
        
        # Create payment as PENDING
        payment = serializer.save(status=Payment.Status.PENDING)
        
        # MOCK PAYMENT PROCESSING
        # In real world, we would call Stripe/PayPal here.
        success = True # Simulate success
        
        if success:
            payment.status = Payment.Status.COMPLETED
            payment.transaction_id = str(uuid.uuid4())
            payment.save()
            
            # Update Order Status
            # If status was RECEIVED, maybe move to PREPARATION? 
            # Or keep as RECEIVED but marked as Paid?
            # User requirement: "Order statuses: Order received, Order in preparation..."
            # Let's assume Order is created -> RECEIVED.
            # Payment doesn't necessarily change status to PREPARATION (Studio does that).
            # But we can consider it "Confirmed".
            pass
        else:
            payment.status = Payment.Status.FAILED
            payment.save()
