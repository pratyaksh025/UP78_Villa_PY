from django.db import models

# 1. Model for your Menu (Unchanged)
class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('Indian', 'Indian'),
        ('Chinese', 'Chinese'),
        ('Rice & Biryani', 'Rice & Biryani'),
        ('Breads', 'Breads'),
        ('Desserts', 'Desserts'),
        ('Beverages', 'Beverages'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    imageUrl = models.URLField(max_length=300)
    def __str__(self):
        return self.name

# 2. Model for Table Reservations (Unchanged)
class Reservation(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    date = models.DateField()
    time = models.TimeField()
    guests = models.IntegerField()
    notes = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Reservation for {self.name} on {self.date}"

# 3. Model for Hall Bookings (UPDATED)
class HallBooking(models.Model):
    eventName = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    date = models.DateField()
    guests = models.IntegerField()
    requirements = models.TextField(blank=True, null=True)
    totalAmount = models.DecimalField(max_digits=10, decimal_places=2)
    # --- UPDATED: We now link to the real coupon model ---
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Hall Booking for {self.eventName} on {self.date}"

# 4. Model for Feedback (UPDATED)
class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField(blank=True, null=True)
    # --- NEW: Added rating field ---
    rating = models.IntegerField(default=5) # 1 to 5 stars
    submitted_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Feedback from {self.name} (Rating: {self.rating})"

# 5. Order Model (UPDATED)
class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PREPARING', 'Preparing'),
        ('READY', 'Ready'),
        ('SERVED', 'Served'),
    ]
    table_number = models.CharField(max_length=10)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # --- NEW: Link to the coupon used ---
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Order {self.id} for Table {self.table_number}"

# 6. OrderItem Model (Unchanged)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"

# 7. --- NEW: Coupon Model ---
class Coupon(models.Model):
    TYPE_CHOICES = [
        ('CART', 'Cart Order'),
        ('HALL', 'Hall Booking'),
    ]
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, help_text="e.g., 10 for 10% off")
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='CART')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} ({self.discount_percent}% off {self.type})"