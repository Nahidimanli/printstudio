from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.views import View
from django.utils.decorators import method_decorator

from apps.users.models import User
from apps.studios.models import StudioProfile, Service
from apps.orders.models import Order, OrderItem

# For simplicity, using request.POST directly or standard AuthView but let's build custom for control.

def web_logout(request):
    logout(request)
    return redirect('web_login')

class WebLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if request.user.role == User.Role.STUDIO:
                return redirect('studio_dashboard')
            # Default for customers and others is to stay on previous page or go to landing/order
            # For now, let's redirect to landing page so they can continue browsing
            return redirect('landing_page')
        return render(request, 'web/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            if user.role == User.Role.STUDIO:
                return redirect('studio_dashboard')
            else:
                 # Customers go back to browsing/landing
                 return redirect('/')
        
        messages.error(request, 'Invalid credentials')
        return render(request, 'web/login.html')

class LandingPageView(View):
    def get(self, request):
        popular_products = Service.objects.filter(is_active=True).select_related('studio')[:4]
        verified_studios = StudioProfile.objects.all()[:4]
        return render(request, 'web/landing.html', {
            'popular_products': popular_products,
            'verified_studios': verified_studios
        })

class ProductListView(View):
    def get(self, request):
        products = Service.objects.filter(is_active=True).select_related('studio')
        return render(request, 'web/product_list.html', {'products': products})

class StudioListView(View):
    def get(self, request):
        studios = StudioProfile.objects.all()
        # Basic filtering
        query = request.GET.get('q')
        if query:
            studios = studios.filter(business_name__icontains=query)
        return render(request, 'web/studio_list.html', {'studios': studios})

class StudioDetailView(View):
    def get(self, request, id):
        studio = get_object_or_404(StudioProfile, id=id)
        services = studio.services.filter(is_active=True)
        return render(request, 'web/studio_detail.html', {
            'studio': studio,
            'services': services
        })

from django.http import JsonResponse
class StudioMapAPI(View):
    def get(self, request):
        studios = StudioProfile.objects.all()
        data = []
        for s in studios:
            data.append({
                'id': s.id,
                'name': s.business_name,
                'lat': s.latitude,
                'lng': s.longitude,
                'address': s.address,
                'url': f"/studios/{s.id}/" # Hardcoded for simplicity, usually reverse()
            })
        return JsonResponse(data, safe=False)

class BecomeSellerView(View):
    def get(self, request):
        return render(request, 'web/become_seller.html')


@method_decorator(login_required, name='dispatch')
class CustomerOrderView(View):
    def get(self, request):
        if request.user.role != User.Role.CUSTOMER:
            return redirect('web_login')
            
        studios = StudioProfile.objects.all().prefetch_related('services')
        orders = Order.objects.filter(customer=request.user).order_by('-created_at')
        return render(request, 'web/customer_order.html', {'studios': studios, 'orders': orders})

    def post(self, request):
        if request.user.role != User.Role.CUSTOMER:
            return redirect('web_login')

        service_id = request.POST.get('service_id')
        quantity = int(request.POST.get('quantity', 1))
        note = request.POST.get('note', '')

        if not service_id:
            messages.error(request, 'Please select a service.')
            return redirect('customer_order')

        service = get_object_or_404(Service, id=service_id)
        
        with transaction.atomic():
            order = Order.objects.create(
                customer=request.user,
                studio=service.studio,
                total_price=service.price * quantity,
                note=note
            )
            OrderItem.objects.create(
                order=order,
                service=service,
                price=service.price,
                quantity=quantity
            )
        
        messages.success(request, 'Order placed successfully!')
        return redirect('customer_order')

@method_decorator(login_required, name='dispatch')
class StudioDashboardView(View):
    def get(self, request):
        if request.user.role != User.Role.STUDIO:
            return redirect('web_login')
            
        try:
            profile = request.user.studio_profile
            orders = Order.objects.filter(studio=profile).order_by('-created_at')
        except StudioProfile.DoesNotExist:
            orders = []
            messages.warning(request, "Studio profile missing.")

        return render(request, 'web/studio_dashboard.html', {'orders': orders})

@login_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        
        # Security check
        if request.user.role == User.Role.STUDIO and order.studio.user == request.user:
            new_status = request.POST.get('status')
            if new_status in Order.Status.values:
                order.status = new_status
                order.save()
                messages.success(request, f"Order #{order.id} updated to {new_status}")
            else:
                messages.error(request, "Invalid status.")
        else:
            messages.error(request, "Permission denied.")
            
    return redirect('studio_dashboard')
