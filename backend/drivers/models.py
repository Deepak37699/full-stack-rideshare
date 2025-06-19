from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator

class Driver(models.Model):
    """Driver profile model"""
    
    VEHICLE_TYPE_CHOICES = [
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('hatchback', 'Hatchback'),
        ('luxury', 'Luxury'),
        ('bike', 'Bike'),
    ]
    
    STATUS_CHOICES = [
        ('offline', 'Offline'),
        ('online', 'Online'),
        ('busy', 'Busy'),
        ('unavailable', 'Unavailable'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='driver_profile')
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry = models.DateField()
    
    # Driver status and verification
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=False)
    background_check_status = models.CharField(max_length=20, default='pending')
    
    # Location tracking
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)
    
    # Document uploads
    vehicle_documents = models.FileField(upload_to='driver_documents/', null=True, blank=True)
    
    # Financial and rating
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Driver: {self.user.username}"
    
    @property
    def rating_average(self):
        """Calculate average rating from completed rides"""
        from rides.models import Ride
        ratings = Ride.objects.filter(
            driver=self, 
            status='completed',
            rating_by_rider__isnull=False
        ).values_list('rating_by_rider', flat=True)
        
        if ratings:
            return sum(ratings) / len(ratings)
        return 0.0
    
    @property
    def total_rides(self):
        """Get total number of completed rides"""
        from rides.models import Ride
        return Ride.objects.filter(driver=self, status='completed').count()


class Vehicle(models.Model):
    """Vehicle model for drivers"""
    
    VEHICLE_TYPE_CHOICES = [
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('hatchback', 'Hatchback'),
        ('luxury', 'Luxury'),
        ('bike', 'Bike'),
    ]
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='vehicles')
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    color = models.CharField(max_length=30)
    license_plate = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES)
    seats = models.PositiveIntegerField(default=4)
    
    # Vehicle registration and insurance
    registration_number = models.CharField(max_length=100)
    insurance_expiry = models.DateField()
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.make} {self.model} ({self.license_plate})"


class DriverDocument(models.Model):
    """Driver document uploads"""
    
    DOCUMENT_TYPE_CHOICES = [
        ('license', 'Driver License'),
        ('insurance', 'Insurance Document'),
        ('registration', 'Vehicle Registration'),
        ('permit', 'Commercial Permit'),
        ('background_check', 'Background Check'),
    ]
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    document_file = models.FileField(upload_to='driver_documents/')
    is_verified = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['driver', 'document_type']
    
    def __str__(self):
        return f"{self.driver.user.username} - {self.document_type}"
