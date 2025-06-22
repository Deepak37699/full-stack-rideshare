from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from typing import Optional
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

# Smart Ride Features Models

class FavoriteLocation(models.Model):
    """Store user's favorite locations for quick selection"""
    
    LOCATION_TYPE_CHOICES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('favorite', 'Favorite'),
        ('recent', 'Recent'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorite_locations')
    name = models.CharField(max_length=100)  # e.g., "Home", "Office", "Mall"
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPE_CHOICES, default='favorite')
    use_count = models.IntegerField(default=0)  # Track usage for smart suggestions
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'name']
        ordering = ['-use_count', '-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class RideTemplate(models.Model):
    """Store frequently used ride routes as templates"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ride_templates')
    name = models.CharField(max_length=100)  # e.g., "Home to Office", "Daily Commute"
    
    # Pickup details
    pickup_name = models.CharField(max_length=100)
    pickup_address = models.TextField()
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    # Destination details
    destination_name = models.CharField(max_length=100)
    destination_address = models.TextField()
    destination_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    destination_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    # Ride preferences
    preferred_ride_type = models.CharField(max_length=20, choices=RideRequest.RIDE_TYPE_CHOICES, default='standard')
    special_instructions = models.TextField(blank=True)
    
    # Usage tracking
    use_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['user', 'name']
        ordering = ['-use_count', '-last_used']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class ScheduledRide(models.Model):
    """Store rides scheduled for future dates/times"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    RECURRING_CHOICES = [
        ('none', 'One-time'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('weekdays', 'Weekdays Only'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scheduled_rides')
    
    # Ride details (can reference a template)
    ride_template = models.ForeignKey(RideTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Pickup and destination (override template if needed)
    pickup_address = models.TextField()
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    destination_address = models.TextField()
    destination_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    destination_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    # Scheduling details
    scheduled_datetime = models.DateTimeField()
    recurring_pattern = models.CharField(max_length=20, choices=RECURRING_CHOICES, default='none')
    recurring_end_date = models.DateField(null=True, blank=True)
    
    # Ride preferences
    ride_type = models.CharField(max_length=20, choices=RideRequest.RIDE_TYPE_CHOICES, default='standard')
    estimated_fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    special_instructions = models.TextField(blank=True)
    
    # Advanced scheduling options
    advance_booking_time = models.IntegerField(default=15)  # minutes before scheduled time to start looking for driver
    auto_confirm = models.BooleanField(default=True)  # Auto-confirm when driver found
    max_wait_time = models.IntegerField(default=5)  # minutes to wait for driver confirmation
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    actual_ride = models.ForeignKey(Ride, on_delete=models.SET_NULL, null=True, blank=True)  # Link to actual ride when created
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
      # Notifications
    notification_sent = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['scheduled_datetime']
    
    def __str__(self):
        return f"Scheduled ride for {self.user.username} at {self.scheduled_datetime}"
    
    def is_due_for_booking(self):
        """Check if it's time to start looking for a driver"""
        now = timezone.now()
        booking_time = self.scheduled_datetime - timedelta(minutes=self.advance_booking_time)
        return now >= booking_time and self.status == 'scheduled'
    
    def is_expired(self):
        """Check if the scheduled ride has expired"""
        now = timezone.now()
        expiry_time = self.scheduled_datetime + timedelta(minutes=self.max_wait_time)
        return now > expiry_time and self.status in ['scheduled', 'confirmed']


class SmartSuggestion(models.Model):
    """AI-powered ride suggestions based on user patterns"""
    
    SUGGESTION_TYPE_CHOICES = [
        ('routine', 'Routine Ride'),
        ('location', 'Popular Destination'),
        ('time', 'Optimal Time'),
        ('route', 'Alternative Route'),
        ('promotion', 'Promotional Offer'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='smart_suggestions')
    suggestion_type = models.CharField(max_length=20, choices=SUGGESTION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Suggested ride details
    suggested_pickup_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    suggested_pickup_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    suggested_pickup_address = models.TextField(blank=True)
    
    suggested_destination_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    suggested_destination_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    suggested_destination_address = models.TextField(blank=True)
    
    suggested_time = models.DateTimeField(null=True, blank=True)
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)  # 0.0 to 1.0
    
    # Tracking
    is_active = models.BooleanField(default=True)
    was_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-confidence_score', '-created_at']
    
    def __str__(self):
        return f"Suggestion for {self.user.username}: {self.title}"
