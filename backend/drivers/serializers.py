from rest_framework import serializers
from .models import Driver, Vehicle
from accounts.serializers import UserSerializer

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = (
            'id', 'make', 'model', 'year', 'color',
            'license_plate', 'vehicle_type', 'seats',
            'is_active', 'registration_number',
            'insurance_expiry', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

class DriverSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    vehicles = VehicleSerializer(many=True, read_only=True)
    rating_average = serializers.ReadOnlyField()
    total_rides = serializers.ReadOnlyField()
    
    class Meta:
        model = Driver
        fields = (
            'id', 'user', 'license_number', 'license_expiry',
            'is_verified', 'is_available', 'vehicle_documents',
            'background_check_status', 'rating_average', 'total_rides',
            'total_earnings', 'current_latitude', 'current_longitude',
            'last_location_update', 'created_at', 'updated_at', 'vehicles'
        )
        read_only_fields = (
            'id', 'user', 'is_verified', 'background_check_status',
            'total_earnings', 'created_at', 'updated_at'
        )

class DriverRegistrationSerializer(serializers.ModelSerializer):
    user_data = UserSerializer()
    
    class Meta:
        model = Driver
        fields = (
            'user_data', 'license_number', 'license_expiry',
            'vehicle_documents'
        )
    
    def create(self, validated_data):
        user_data = validated_data.pop('user_data')
        user_data['user_type'] = 'driver'
        
        # Create user first
        from accounts.models import User
        user = User.objects.create_user(**user_data)
        
        # Create driver profile
        driver = Driver.objects.create(user=user, **validated_data)
        return driver

class DriverLocationUpdateSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    is_available = serializers.BooleanField(required=False)

class DriverAvailabilitySerializer(serializers.Serializer):
    is_available = serializers.BooleanField()

class DriverEarningsSerializer(serializers.Serializer):
    total_earnings = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    today_earnings = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    week_earnings = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    month_earnings = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_rides = serializers.IntegerField(read_only=True)
    rating_average = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

class VehicleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = (
            'make', 'model', 'year', 'color',
            'license_plate', 'vehicle_type', 'seats',
            'registration_number', 'insurance_expiry'
        )
    
    def create(self, validated_data):
        driver = self.context['request'].user.driver_profile
        validated_data['driver'] = driver
        return super().create(validated_data)
