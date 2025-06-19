from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class RideRequest(models.Model):
    """Model for ride requests before they are matched with drivers"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    RIDE_TYPE_CHOICES = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('luxury', 'Luxury'),
        ('shared', 'Shared'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ride_requests')
    
    # Pickup and destination
    pickup_address = models.TextField()
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    destination_address = models.TextField()
    destination_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    destination_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    # Ride details
    ride_type = models.CharField(max_length=20, choices=RIDE_TYPE_CHOICES, default='standard')
    estimated_fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # in kilometers
    special_instructions = models.TextField(blank=True)
    
    # Request status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"Ride Request {self.id} - {self.rider.username}"


class Ride(models.Model):
    """Main ride model"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    RIDE_TYPE_CHOICES = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('luxury', 'Luxury'),
        ('shared', 'Shared'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ride_request = models.OneToOneField(RideRequest, on_delete=models.CASCADE, related_name='ride', null=True, blank=True)
    rider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rides_as_rider')
    driver = models.ForeignKey('drivers.Driver', on_delete=models.SET_NULL, null=True, blank=True, related_name='rides_as_driver')
    
    # Pickup and destination
    pickup_address = models.TextField()
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    destination_address = models.TextField()
    destination_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    destination_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    # Ride details
    ride_type = models.CharField(max_length=20, choices=RIDE_TYPE_CHOICES, default='standard')
    fare = models.DecimalField(max_digits=10, decimal_places=2)
    distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # in kilometers
    
    # Status and timing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Additional info
    cancellation_reason = models.TextField(blank=True)
    driver_notes = models.TextField(blank=True)
    rider_notes = models.TextField(blank=True)
    rating_by_rider = models.PositiveIntegerField(null=True, blank=True)  # 1-5 rating
    rating_by_driver = models.PositiveIntegerField(null=True, blank=True)  # 1-5 rating
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Ride {self.id} - {self.rider.username} to {self.destination_address[:30]}"
    
    @property
    def duration_minutes(self):
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds() / 60)
        return None
    
    def accept_ride(self, driver):
        """Accept the ride with a driver"""
        self.driver = driver
        self.status = 'accepted'
        self.accepted_at = timezone.now()
        self.save()
    
    def start_ride(self):
        """Start the ride"""
        self.status = 'in_progress'
        self.started_at = timezone.now()
        self.save()
    
    def complete_ride(self, actual_fare=None, actual_distance=None):
        """Complete the ride"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if actual_fare:
            self.fare = actual_fare
        if actual_distance:
            self.distance = actual_distance
        self.save()
    
    def cancel_ride(self, reason=""):
        """Cancel the ride"""
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.cancellation_reason = reason
        self.save()


class RideLocation(models.Model):
    """Track real-time location during ride"""
    
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timestamp = models.DateTimeField(auto_now_add=True)
    speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # km/h
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Location for Ride {self.ride.id} at {self.timestamp}"
