from rest_framework import serializers
from .models import Payment, Order

class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), source='order', write_only=True
    )
    
    class Meta:
        model = Payment
        fields = ('id', 'order', 'order_id', 'amount', 'transaction_id', 'status', 'created_at')
        read_only_fields = ('status', 'transaction_id', 'amount', 'order')

    def validate_order_id(self, value):
        if hasattr(value, 'payment'):
             raise serializers.ValidationError("Order is already paid or payment is pending.")
        return value

    def create(self, validated_data):
        order = validated_data['order']
        # Auto-set amount from order
        validated_data['amount'] = order.total_price
        return super().create(validated_data)
