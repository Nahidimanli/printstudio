from django.urls import path
from .views import WebLoginView, web_logout, CustomerOrderView, StudioDashboardView, update_order_status, LandingPageView, ProductListView, StudioListView, BecomeSellerView, StudioDetailView, StudioMapAPI

urlpatterns = [
    path('', LandingPageView.as_view(), name='landing_page'),
    path('products/', ProductListView.as_view(), name='product_list'),
    path('studios/', StudioListView.as_view(), name='studio_list'),
    path('studios/<int:id>/', StudioDetailView.as_view(), name='studio_detail'),
    path('api/studios/map/', StudioMapAPI.as_view(), name='studio_map_api'),
    path('become-seller/', BecomeSellerView.as_view(), name='become_seller'),
    path('login/', WebLoginView.as_view(), name='web_login'),
    path('logout/', web_logout, name='web_logout'),
    path('customer/order/', CustomerOrderView.as_view(), name='customer_order'),
    path('studio/dashboard/', StudioDashboardView.as_view(), name='studio_dashboard'),
    path('order/<int:order_id>/update/', update_order_status, name='update_order_status'),
]
