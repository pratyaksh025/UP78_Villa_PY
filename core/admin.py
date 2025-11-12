from django.contrib import admin
from .models import (
    MenuItem, Reservation, HallBooking, Feedback, 
    Order, OrderItem, Coupon
)

# This allows you to see OrderItems "inside" the Order page in the admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 # Don't show extra empty forms

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'table_number', 'status', 'total_price', 'coupon', 'created_at')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]

# --- NEW: Admin view for Coupons ---
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'type', 'discount_percent', 'is_active')
    list_filter = ('type', 'is_active')

# --- NEW: Admin view for Feedback ---
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'rating', 'submitted_at')
    list_filter = ('rating', 'submitted_at')

# Register your models
admin.site.register(MenuItem)
admin.site.register(Reservation)
admin.site.register(HallBooking)
admin.site.register(Feedback, FeedbackAdmin) # Use the custom FeedbackAdmin
admin.site.register(Order, OrderAdmin) # Use the custom OrderAdmin
admin.site.register(Coupon, CouponAdmin) # Use the custom CouponAdmin