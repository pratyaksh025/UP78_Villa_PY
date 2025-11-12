from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), 
    path('reservation/', views.reservation_view, name='reservation'),
    path('hall-booking/', views.hall_booking_view, name='hall-booking'),
    
    # --- ADD THE FOLLOWING 4 LINES ---
    path('add-to-cart/', views.add_to_cart_view, name='add-to-cart'),
    path('cart/', views.cart_view, name='cart'),
    path('place-order/', views.place_order_view, name='place-order'),
    path('qr-generator/', views.qr_generator_view, name='qr-generator'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('apply-coupon/', views.apply_coupon_view, name='apply-coupon'),
    path('kitchen/', views.kitchen_view, name='kitchen-dashboard'),
    path('update-order-status/<int:order_id>/', views.update_order_status_view, name='update-order-status'),
]