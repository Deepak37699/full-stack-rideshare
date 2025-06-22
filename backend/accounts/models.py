from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid

class User(AbstractUser):
    """Custom User model for the ride sharing application"""
    
    USER_TYPE_CHOICES = [
        ('rider', 'Rider'),
        ('driver', 'Driver'),
        ('admin', 'Admin'),
    ]
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    # Use phone number as the username field
    username = models.CharField(
        max_length=17, 
        unique=True,
        validators=[phone_regex],
        help_text="Phone number used for authentication"
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='rider')
    phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Location fields
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)
    
    # Override the USERNAME_FIELD to use phone number
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email', 'user_type']
    
    def save(self, *args, **kwargs):
        # Ensure username and phone_number are the same
        if self.phone_number:
            self.username = self.phone_number
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.phone_number} ({self.user_type})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_driver(self):
        return self.user_type == 'driver'
    
    @property
    def is_rider(self):
        return self.user_type == 'rider'


class UserProfile(models.Model):
    """Extended profile information for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=17, blank=True)
    preferred_language = models.CharField(max_length=10, default='en')
    notification_preferences = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"


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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
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
