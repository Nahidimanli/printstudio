from django.conf import settings
from apps.studios.models import Service

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, service, quantity=1):
        service_id = str(service.id)
        if service_id not in self.cart:
            self.cart[service_id] = {
                'quantity': 0,
                'price': str(service.price),
                'name': service.name,
                'studio': service.studio.business_name
            }
        self.cart[service_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, service):
        service_id = str(service.id)
        if service_id in self.cart:
            del self.cart[service_id]
            self.save()

    def __iter__(self):
        service_ids = self.cart.keys()
        services = Service.objects.filter(id__in=service_ids)
        cart = self.cart.copy()
        
        for service in services:
            cart[str(service.id)]['service'] = service

        for item in cart.values():
            item['price'] = float(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def get_total_price(self):
        return sum(float(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session['cart']
        self.save()
