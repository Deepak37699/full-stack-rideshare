from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class Review(models.Model):
    """Model for ride reviews"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ride = models.ForeignKey('rides.Ride', on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    reviewee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_received')
    
    rating = models.PositiveIntegerField()  # 1-5 stars
    comment = models.TextField(blank=True)
    
    # Review categories for drivers
    cleanliness = models.PositiveIntegerField(null=True, blank=True)  # 1-5
    communication = models.PositiveIntegerField(null=True, blank=True)  # 1-5
    driving_quality = models.PositiveIntegerField(null=True, blank=True)  # 1-5
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('ride', 'reviewer')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.reviewee.username} - {self.rating} stars"


class Notification(models.Model):
    """Model for push notifications"""
    
    NOTIFICATION_TYPES = [
        ('ride_request', 'Ride Request'),
        ('ride_accepted', 'Ride Accepted'),
        ('ride_started', 'Ride Started'),
        ('ride_completed', 'Ride Completed'),
        ('ride_cancelled', 'Ride Cancelled'),
        ('driver_arrived', 'Driver Arrived'),
        ('payment_completed', 'Payment Completed'),
        ('review_received', 'Review Received'),
        ('promo_available', 'Promo Available'),
        ('system_update', 'System Update'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    
    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    # Optional related objects
    ride = models.ForeignKey('rides.Ride', on_delete=models.CASCADE, null=True, blank=True)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"


class PromoCode(models.Model):
    """Model for promotional codes"""
    
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    min_ride_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    max_uses_per_user = models.PositiveIntegerField(default=1)
    
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.title}"
    
    @property
    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_until
    
    @property
    def usage_count(self):
        return self.promo_uses.count()


class PromoCodeUse(models.Model):
    """Track promo code usage"""
    
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, related_name='promo_uses')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='promo_uses')
    ride = models.ForeignKey('rides.Ride', on_delete=models.CASCADE, related_name='promo_uses')
    
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('promo_code', 'user', 'ride')
        ordering = ['-used_at']
    
    def __str__(self):
        return f"{self.user.username} used {self.promo_code.code} on {self.ride.id}"


class EmergencyContact(models.Model):
    """Emergency contacts for safety features"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    relationship = models.CharField(max_length=50)
    
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.relationship}) - {self.user.username}"


class SOS(models.Model):
    """SOS alerts for emergency situations"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('resolved', 'Resolved'),
        ('false_alarm', 'False Alarm'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sos_alerts')
    ride = models.ForeignKey('rides.Ride', on_delete=models.CASCADE, null=True, blank=True, related_name='sos_alerts')
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    message = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"SOS Alert by {self.user.username} at {self.created_at}"
