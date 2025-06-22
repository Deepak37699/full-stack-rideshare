from django.db import models
from django.conf import settings
import uuid

class PaymentMethod(models.Model):
    """User payment methods"""
    
    PAYMENT_TYPE_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
        ('cash', 'Cash'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_methods')
    method_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    is_default = models.BooleanField(default=False)
    
    # Card details (encrypted in production)
    card_number = models.CharField(max_length=255, blank=True)  # This should be encrypted
    cardholder_name = models.CharField(max_length=100, blank=True)
    expiry_month = models.PositiveIntegerField(null=True, blank=True)
    expiry_year = models.PositiveIntegerField(null=True, blank=True)
      # External wallet details
    external_id = models.CharField(max_length=255, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'method_type', 'external_id']
    
    def __str__(self):
        if self.method_type == 'card' and self.card_number:
            return f"Card ending in {self.card_number[-4:]}"
        # Django's get_FOO_display() method for choices field
        return getattr(self, 'get_method_type_display', lambda: self.method_type)()


class Payment(models.Model):
    """Payment transactions"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('ride_fare', 'Ride Fare'),
        ('tip', 'Tip'),
        ('refund', 'Refund'),
        ('cancellation_fee', 'Cancellation Fee'),
        ('driver_payout', 'Driver Payout'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    ride = models.ForeignKey('rides.Ride', on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # External payment processor details
    transaction_id = models.CharField(max_length=255, blank=True)
    gateway_response = models.JSONField(default=dict)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    
    failure_reason = models.TextField(blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.id} - {self.amount} {self.currency} ({self.status})"


class DriverEarnings(models.Model):
    """Track driver earnings and payouts"""
    
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='earnings')
    ride = models.OneToOneField('rides.Ride', on_delete=models.CASCADE, related_name='driver_earnings')
    
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_commission = models.DecimalField(max_digits=8, decimal_places=2)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tip_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    is_paid_out = models.BooleanField(default=False)
    paid_out_at = models.DateTimeField(null=True, blank=True)
    payout_transaction_id = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Earnings for {self.driver.username} - Ride {self.ride.id}"


class Refund(models.Model):
    """Refund requests and processing"""
    
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('processed', 'Processed'),
        ('rejected', 'Rejected'),
    ]
    
    REASON_CHOICES = [
        ('ride_cancelled', 'Ride Cancelled'),
        ('driver_no_show', 'Driver No Show'),
        ('poor_service', 'Poor Service'),
        ('overcharge', 'Overcharge'),
        ('technical_issue', 'Technical Issue'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='refund')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_refunds')
    external_refund_id = models.CharField(max_length=255, blank=True)
    
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    admin_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Refund {self.id} - {self.amount} ({self.status})"
