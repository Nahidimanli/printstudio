from rest_framework import serializers
from .models import Order, OrderItem, OrderFile
from apps.studios.models import Service

class OrderItemSerializer(serializers.ModelSerializer):
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(), source='service', write_only=True
    )
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ('id', 'service_id', 'service_name', 'price', 'quantity')
        read_only_fields = ('price',)

class OrderFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderFile
        fields = ('id', 'file', 'uploaded_at')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    files = OrderFileSerializer(many=True, read_only=True)
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    studio_name = serializers.CharField(source='studio.business_name', read_only=True)
    studio_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'customer', 'customer_username', 'studio', 'studio_id', 'studio_name',
            'status', 'total_price', 'note', 'items', 'files', 'created_at'
        )
        read_only_fields = ('customer', 'studio', 'total_price', 'status', 'created_at')

    def validate(self, attrs):
        studio_id = attrs.get('studio_id')
        items_data = attrs.get('items')
        
        if not items_data:
            raise serializers.ValidationError("Order must contain at least one service.")

        # Validate all services belong to the selected studio
        for item in items_data:
            service = item['service']
            if service.studio.id != studio_id:
                raise serializers.ValidationError(
                    f"Service '{service.name}' does not belong to the selected studio."
                )
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        studio_id = validated_data.pop('studio_id')
        
        # Calculate total price
        total_price = 0
        for item in items_data:
            service = item['service']
            quantity = item.get('quantity', 1)
            total_price += service.price * quantity

        order = Order.objects.create(
            studio_id=studio_id,
            total_price=total_price,
            **validated_data
        )

        for item in items_data:
            OrderItem.objects.create(
                order=order,
                service=item['service'],
                price=item['service'].price,
                quantity=item.get('quantity', 1)
            )
        
        return order
