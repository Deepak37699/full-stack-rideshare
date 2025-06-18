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
    vehicle_make = models.CharField(max_length=50)
    vehicle_model = models.CharField(max_length=50)
    vehicle_year = models.PositiveIntegerField()
    vehicle_color = models.CharField(max_length=30)
    vehicle_plate = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES)
    
    # Insurance and documents
    insurance_policy = models.CharField(max_length=100)
    insurance_expiry = models.DateField()
    vehicle_registration = models.CharField(max_length=100)
    
    # Driver status and rating
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    total_rides = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    
    # Financial
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Driver: {self.user.username} - {self.vehicle_make} {self.vehicle_model}"
    
    @property
    def is_available(self):
        return self.status == 'online' and self.is_approved
    
    def update_rating(self, new_rating):
        """Update driver rating with new rating"""
        current_total = self.rating * self.total_rides
        self.total_rides += 1
        self.rating = (current_total + new_rating) / self.total_rides
        self.save()


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
