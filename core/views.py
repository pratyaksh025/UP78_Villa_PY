from django.shortcuts import render, redirect
# We no longer need send_mail or settings
from .models import MenuItem, Reservation, HallBooking, Order, OrderItem, Feedback, Coupon
import qrcode
import io
from django.http import HttpResponse
import datetime
from decimal import Decimal
from django.db.models import Q
from django.contrib.auth.decorators import login_required

# --- 1. Homepage View (Index) ---
def index(request):
    table_number = request.GET.get('table')
    
    if table_number:
        request.session['table_number'] = table_number
        print(f"Session set for table: {table_number}")
    else:
        table_number = request.session.get('table_number', None)
    
    all_menu_items = MenuItem.objects.all()
    cart = request.session.get('cart', {})
    cart_item_count = sum(cart.values())
    
    context = {
        'menu_items': all_menu_items,
        'table_number': table_number,
        'cart_item_count': cart_item_count,
    }
    return render(request, 'index.html', context)

# --- 2. Reservation View (Email Removed) ---
def reservation_view(request):
    context = {}
    if request.method == 'POST':
        # 1. Get the data from the form
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        time = request.POST.get('time')
        guests = request.POST.get('guests')
        notes = request.POST.get('notes')

        # 2. Save the data to the database
        reservation = Reservation.objects.create(
            name=name,
            phone=phone,
            date=date,
            time=time,
            guests=guests,
            notes=notes
        )
        
        # 3. (Email sending is now removed)

        # 4. Show a success message
        context = {'success_message': 'Your reservation has been saved! We will check our records to confirm.'}
        return render(request, 'reservation.html', context)

    context['today'] = datetime.date.today().isoformat()
    return render(request, 'reservation.html', context)

# --- 3. Hall Booking View (Email Removed) ---
def hall_booking_view(request):
    context = {}
    if request.method == 'POST':
        # 1. Get the data
        eventName = request.POST.get('eventName')
        contact = request.POST.get('contact')
        date = request.POST.get('date')
        guests = request.POST.get('guests')
        requirements = request.POST.get('requirements')
        coupon_code = request.POST.get('coupon_code')
        
        base_price = Decimal('49999.00')
        per_guest_price = Decimal('399.00')
        total_amount = base_price + (Decimal(guests) * per_guest_price)
        
        coupon_obj = None
        discount_amount = Decimal('0.00')
        if coupon_code:
            try:
                coupon_obj = Coupon.objects.get(code__iexact=coupon_code, type='HALL', is_active=True)
                discount_amount = total_amount * (coupon_obj.discount_percent / Decimal('100.00'))
                total_amount -= discount_amount
            except Coupon.DoesNotExist:
                pass
        
        # 2. Save to database
        booking = HallBooking.objects.create(
            eventName=eventName, contact=contact, date=date, guests=guests,
            requirements=requirements, totalAmount=total_amount, coupon=coupon_obj
        )
        
        # 3. (Email sending is now removed)

        # 4. Show a success message
        context = {'success_message': 'Your hall booking has been saved! Our team will check our records to confirm.'}

    context['today'] = datetime.date.today().isoformat()
    return render(request, 'hall_booking.html', context)

# --- 4. QR Generator View ---
def qr_generator_view(request):
    context = {}
    if request.method == 'POST':
        table_number = request.POST.get('table_number')
        if table_number:
            qr_url = request.build_absolute_uri(f"/?table={table_number}")
            img = qrcode.make(qr_url)
            buf = io.BytesIO()
            img.save(buf)
            buf.seek(0)
            return HttpResponse(buf, content_type='image/png')
            
    return render(request, 'qr_generator.html')

# --- 5. Add to Cart View ---
def add_to_cart_view(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        cart = request.session.get('cart', {})
        cart[item_id] = cart.get(item_id, 0) + 1
        request.session['cart'] = cart
        print(f"Updated cart: {cart}")
    return redirect('index')

# --- 6. Cart View ---
def cart_view(request):
    cart = request.session.get('cart', {})
    table_number = request.session.get('table_number', None)
    coupon_id = request.session.get('coupon_id', None)
    
    cart_items = []
    subtotal = Decimal('0.00')
    
    for item_id, quantity in cart.items():
        try:
            item = MenuItem.objects.get(id=item_id)
            item_total = item.price * quantity
            subtotal += item_total
            cart_items.append({
                'id': item.id, 'name': item.name, 'price': item.price,
                'quantity': quantity, 'item_total': item_total, 'imageUrl': item.imageUrl
            })
        except MenuItem.DoesNotExist:
            pass
    
    coupon_obj = None
    discount_amount = Decimal('0.00')
    if coupon_id:
        try:
            coupon_obj = Coupon.objects.get(id=coupon_id, type='CART', is_active=True)
            discount_amount = subtotal * (coupon_obj.discount_percent / Decimal('100.00'))
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
    
    final_total = subtotal - discount_amount
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'final_total': final_total,
        'coupon': coupon_obj,
        'table_number': table_number,
    }
    return render(request, 'cart.html', context)
    
# --- 7. Place Order View ---
def place_order_view(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        table_number = request.session.get('table_number', None)
        coupon_id = request.session.get('coupon_id', None)
        
        if not table_number or not cart:
            return redirect('cart') 

        subtotal = Decimal('0.00')
        for item_id, quantity in cart.items():
            item = MenuItem.objects.get(id=item_id)
            subtotal += item.price * quantity
        
        coupon_obj = None
        discount_amount = Decimal('0.00')
        if coupon_id:
            try:
                coupon_obj = Coupon.objects.get(id=coupon_id, type='CART', is_active=True)
                discount_amount = subtotal * (coupon_obj.discount_percent / Decimal('100.00'))
            except Coupon.DoesNotExist:
                pass
        
        final_total = subtotal - discount_amount

        order = Order.objects.create(
            table_number=table_number,
            total_price=final_total,
            coupon=coupon_obj
        )
        
        for item_id, quantity in cart.items():
            item = MenuItem.objects.get(id=item_id)
            OrderItem.objects.create(
                order=order, menu_item=item, quantity=quantity, price=item.price
            )
            
        request.session['cart'] = {}
        request.session['coupon_id'] = None
        request.session['table_number'] = None
        
        return redirect('index')
        
    return redirect('cart')

# --- 8. Apply Coupon View ---
def apply_coupon_view(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code, type='CART', is_active=True)
            request.session['coupon_id'] = coupon.id
        except Coupon.DoesNotExist:
            pass
    return redirect('cart')

# --- 9. Feedback View ---
def feedback_view(request):
    context = {}
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        rating = request.POST.get('rating')
        message = request.POST.get('message')
        
        Feedback.objects.create(
            name=name, email=email, rating=rating, message=message
        )
        
        context = {'success_message': 'Thank you for your feedback!'}
        
    return render(request, 'feedback.html', context)

# --- 10. Kitchen Dashboard View ---
# @login_required(login_url='/admin/login/')
def kitchen_view(request):
    active_orders = Order.objects.filter(
        Q(status='PENDING') | Q(status='PREPARING')
    ).order_by('created_at')
    
    context = {
        'active_orders': active_orders
    }
    return render(request, 'kitchen.html', context)

# --- 11. Order Status Update View ---
# @login_required(login_url='/admin/login/')
def update_order_status_view(request, order_id):
    if request.method == 'POST':
        try:
            order = Order.objects.get(id=order_id)
            new_status = request.POST.get('new_status')
            
            if new_status in ['PREPARING', 'READY', 'SERVED']:
                order.status = new_status
                order.save()
                
        except Order.DoesNotExist:
            pass
            
    return redirect('kitchen-dashboard')