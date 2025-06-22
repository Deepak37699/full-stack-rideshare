from rest_framework import serializers
from .models import Ride, RideRequest, RideLocation, FavoriteLocation, RideTemplate, ScheduledRide, SmartSuggestion
from accounts.serializers import UserSerializer
from drivers.serializers import DriverSerializer

class RideRequestSerializer(serializers.ModelSerializer):
    rider = UserSerializer(read_only=True)
    estimated_fare = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    distance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = RideRequest
        fields = (
            'id', 'rider', 'pickup_latitude', 'pickup_longitude',
            'pickup_address', 'destination_latitude', 'destination_longitude',
            'destination_address', 'ride_type', 'estimated_fare',
            'distance', 'special_instructions', 'status',
            'requested_at', 'expires_at'
        )
        read_only_fields = ('id', 'rider', 'requested_at', 'expires_at', 'status')
    
    def create(self, validated_data):
        # Calculate estimated fare and distance here
        # For now, we'll set dummy values
        validated_data['estimated_fare'] = 10.00  # Replace with actual calculation
        validated_data['distance'] = 5.0  # Replace with actual calculation
        validated_data['rider'] = self.context['request'].user
        return super().create(validated_data)

class RideSerializer(serializers.ModelSerializer):
    rider = UserSerializer(read_only=True)
    driver = DriverSerializer(read_only=True)
    ride_request = RideRequestSerializer(read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = Ride
        fields = (
            'id', 'ride_request', 'rider', 'driver',
            'pickup_latitude', 'pickup_longitude', 'pickup_address',
            'destination_latitude', 'destination_longitude', 'destination_address',
            'ride_type', 'fare', 'distance', 'status',
            'started_at', 'completed_at', 'cancelled_at',
            'cancellation_reason', 'driver_notes', 'rider_notes',
            'rating_by_rider', 'rating_by_driver', 'duration_minutes'
        )
        read_only_fields = (
            'id', 'ride_request', 'rider', 'started_at',
            'completed_at', 'cancelled_at'
        )
    
    def get_duration_minutes(self, obj):
        if obj.started_at and obj.completed_at:
            duration = obj.completed_at - obj.started_at
            return int(duration.total_seconds() / 60)
        return None

class RideUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = ('status', 'cancellation_reason', 'driver_notes', 'rider_notes')
    
    def validate_status(self, value):
        current_status = self.instance.status if self.instance else None
        user = self.context['request'].user
        
        # Define valid status transitions
        valid_transitions = {
            'pending': ['accepted', 'cancelled'],
            'accepted': ['in_progress', 'cancelled'],
            'in_progress': ['completed', 'cancelled'],
            'completed': [],
            'cancelled': []
        }
        
        if current_status and value not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(f"Cannot change status from {current_status} to {value}")
        
        return value

class RideRatingSerializer(serializers.Serializer):
    ride_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    review = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_ride_id(self, value):
        user = self.context['request'].user
        try:
            ride = Ride.objects.get(id=value)
            if user.user_type == 'rider' and ride.rider != user:
                raise serializers.ValidationError("You can only rate rides you took")
            elif user.user_type == 'driver' and ride.driver.user != user:
                raise serializers.ValidationError("You can only rate rides you drove")
            if ride.status != 'completed':
                raise serializers.ValidationError("You can only rate completed rides")
            return value
        except Ride.DoesNotExist:
            raise serializers.ValidationError("Ride does not exist")

class RideLocationUpdateSerializer(serializers.Serializer):
    ride_id = serializers.IntegerField()
    current_latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    current_longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    
    def validate_ride_id(self, value):
        user = self.context['request'].user
        try:
            ride = Ride.objects.get(id=value)
            if user.user_type != 'driver' or ride.driver.user != user:
                raise serializers.ValidationError("Only the assigned driver can update ride location")
            if ride.status not in ['accepted', 'in_progress']:
                raise serializers.ValidationError("Can only update location for active rides")
            return value
        except Ride.DoesNotExist:
            raise serializers.ValidationError("Ride does not exist")

# Enhanced serializers for new API endpoints

class FareEstimateSerializer(serializers.Serializer):
    """Serializer for fare estimation requests"""
    pickup_latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    pickup_longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    destination_latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    destination_longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    ride_type = serializers.ChoiceField(
        choices=['standard', 'premium', 'luxury', 'shared'],
        default='standard'
    )

class NearbyDriverSerializer(serializers.Serializer):
    """Serializer for nearby driver search"""
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    radius_km = serializers.IntegerField(default=5, min_value=1, max_value=20)

class RideMatchingSerializer(serializers.Serializer):
    """Serializer for ride matching requests"""
    pickup_latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    pickup_longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    pickup_address = serializers.CharField(max_length=500)
    destination_latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    destination_longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    destination_address = serializers.CharField(max_length=500)
    ride_type = serializers.ChoiceField(
        choices=['standard', 'premium', 'luxury', 'shared'],
        default='standard'
    )
    special_instructions = serializers.CharField(max_length=1000, required=False, allow_blank=True)

class GeocodeSerializer(serializers.Serializer):
    """Serializer for geocoding requests"""
    operation = serializers.ChoiceField(choices=['geocode', 'reverse_geocode'])
    address = serializers.CharField(max_length=500, required=False)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)

class EmergencyAlertSerializer(serializers.Serializer):
    """Serializer for emergency alerts"""
    ride_id = serializers.UUIDField()
    alert_type = serializers.ChoiceField(
        choices=['general', 'accident', 'harassment', 'vehicle_breakdown', 'medical'],
        default='general'
    )
    message = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)

class RideLocationSerializer(serializers.ModelSerializer):
    """Serializer for real-time ride location tracking"""
    
    class Meta:
        model = RideLocation
        fields = ('id', 'ride', 'latitude', 'longitude', 'timestamp', 'speed')
        read_only_fields = ('id', 'timestamp')

class DetailedRideSerializer(serializers.ModelSerializer):
    """Enhanced ride serializer with additional details"""
    rider = UserSerializer(read_only=True)
    driver = DriverSerializer(read_only=True)
    locations = RideLocationSerializer(many=True, read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    
    class Meta:
        model = Ride
        fields = (
            'id', 'rider', 'driver', 'pickup_latitude', 'pickup_longitude',
            'pickup_address', 'destination_latitude', 'destination_longitude',
            'destination_address', 'ride_type', 'fare', 'distance',
            'status', 'requested_at', 'accepted_at', 'started_at',
            'completed_at', 'cancelled_at', 'cancellation_reason',
            'driver_notes', 'rider_notes', 'rating_by_rider',
            'rating_by_driver', 'created_at', 'updated_at',
            'locations', 'duration_minutes'
        )

# Smart Ride Features Serializers

class FavoriteLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteLocation
        fields = (
            'id', 'user', 'name', 'address', 'latitude', 'longitude',
            'location_type', 'use_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'use_count', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class RideTemplateSerializer(serializers.ModelSerializer):
    use_count = serializers.ReadOnlyField()
    
    class Meta:
        model = RideTemplate
        fields = (
            'id', 'user', 'name', 'pickup_name', 'pickup_address', 'pickup_latitude', 
            'pickup_longitude', 'destination_name', 'destination_address', 'destination_latitude',
            'destination_longitude', 'preferred_ride_type', 'special_instructions',
            'is_active', 'use_count', 'last_used', 'created_at'
        )
        read_only_fields = ('id', 'user', 'use_count', 'last_used', 'created_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ScheduledRideSerializer(serializers.ModelSerializer):
    ride_template_name = serializers.CharField(source='ride_template.name', read_only=True)
    is_due_for_booking = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = ScheduledRide
        fields = (
            'id', 'user', 'ride_template', 'ride_template_name', 'pickup_address',
            'pickup_latitude', 'pickup_longitude', 'destination_address',
            'destination_latitude', 'destination_longitude', 'scheduled_datetime',
            'recurring_pattern', 'recurring_end_date', 'ride_type', 'estimated_fare',
            'special_instructions', 'advance_booking_time', 'auto_confirm',
            'max_wait_time', 'status', 'actual_ride', 'notification_sent',
            'reminder_sent', 'is_due_for_booking', 'is_expired', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'user', 'actual_ride', 'notification_sent', 'reminder_sent',
            'is_due_for_booking', 'is_expired', 'created_at', 'updated_at'
        )

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_scheduled_datetime(self, value):
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError("Scheduled datetime must be in the future.")
        return value


class SmartSuggestionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SmartSuggestion
        fields = (
            'id', 'user', 'suggestion_type', 'title', 'description',
            'suggested_pickup_lat', 'suggested_pickup_lng', 'suggested_pickup_address',
            'suggested_destination_lat', 'suggested_destination_lng', 'suggested_destination_address',
            'suggested_time', 'confidence_score', 'is_active', 'was_used', 'expires_at', 'created_at'
        )
        read_only_fields = (
            'id', 'user', 'confidence_score', 'created_at'
        )
