from rest_framework import serializers
from .models import Ride, RideRequest
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
