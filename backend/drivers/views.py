from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Driver, Vehicle
from .serializers import (
    DriverSerializer, DriverRegistrationSerializer, DriverLocationUpdateSerializer,
    DriverAvailabilitySerializer, DriverEarningsSerializer, VehicleSerializer,
    VehicleCreateSerializer
)

class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'driver':
            return Driver.objects.filter(user=user)
        # Admin users can see all drivers
        if user.is_staff:
            return Driver.objects.all()
        return Driver.objects.none()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current driver's profile"""
        if request.user.user_type != 'driver':
            return Response(
                {'error': 'Only drivers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            driver = request.user.driver_profile
            serializer = self.get_serializer(driver)
            return Response(serializer.data)
        except Driver.DoesNotExist:
            return Response(
                {'error': 'Driver profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def update_location(self, request):
        """Update driver's current location"""
        if request.user.user_type != 'driver':
            return Response(
                {'error': 'Only drivers can update location'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = DriverLocationUpdateSerializer(data=request.data)
        if serializer.is_valid():
            driver = request.user.driver_profile
            driver.current_latitude = serializer.validated_data['latitude']
            driver.current_longitude = serializer.validated_data['longitude']
            driver.last_location_update = timezone.now()
            
            # Update availability if provided
            if 'is_available' in serializer.validated_data:
                driver.is_available = serializer.validated_data['is_available']
            
            driver.save()
            return Response({'message': 'Location updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def toggle_availability(self, request):
        """Toggle driver availability status"""
        if request.user.user_type != 'driver':
            return Response(
                {'error': 'Only drivers can toggle availability'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = DriverAvailabilitySerializer(data=request.data)
        if serializer.is_valid():
            driver = request.user.driver_profile
            driver.is_available = serializer.validated_data['is_available']
            driver.save()
            
            return Response({
                'message': f"Driver availability set to {'available' if driver.is_available else 'unavailable'}",
                'is_available': driver.is_available
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def earnings(self, request):
        """Get driver earnings summary"""
        if request.user.user_type != 'driver':
            return Response(
                {'error': 'Only drivers can view earnings'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        driver = request.user.driver_profile
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        from rides.models import Ride
        
        # Calculate earnings
        all_rides = Ride.objects.filter(driver=driver, status='completed')
        today_rides = all_rides.filter(completed_at__date=today)
        week_rides = all_rides.filter(completed_at__date__gte=week_start)
        month_rides = all_rides.filter(completed_at__date__gte=month_start)
        
        earnings_data = {
            'total_earnings': driver.total_earnings,
            'today_earnings': today_rides.aggregate(Sum('fare'))['fare__sum'] or 0,
            'week_earnings': week_rides.aggregate(Sum('fare'))['fare__sum'] or 0,
            'month_earnings': month_rides.aggregate(Sum('fare'))['fare__sum'] or 0,
            'total_rides': all_rides.count(),
            'rating_average': all_rides.aggregate(Avg('rating_by_rider'))['rating_by_rider__avg'] or 0,
        }
        
        serializer = DriverEarningsSerializer(earnings_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def nearby_requests(self, request):
        """Get nearby ride requests for available drivers"""
        if request.user.user_type != 'driver':
            return Response(
                {'error': 'Only drivers can view ride requests'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        driver = request.user.driver_profile
        
        if not driver.is_available:
            return Response({'message': 'Driver is not available'})
        
        # Get ride requests within 10km radius (simplified)
        from rides.models import RideRequest
        ride_requests = RideRequest.objects.filter(
            status='pending',
            expires_at__gt=timezone.now()
        )
        
        # TODO: Add distance calculation and filtering
        # For now, return all pending requests
        
        from rides.serializers import RideRequestSerializer
        serializer = RideRequestSerializer(ride_requests, many=True)
        return Response(serializer.data)

class DriverRegistrationView(generics.CreateAPIView):
    serializer_class = DriverRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            driver = serializer.save()
            return Response({
                'message': 'Driver registration successful. Verification pending.',
                'driver': DriverSerializer(driver).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.user_type == 'driver':
            return Vehicle.objects.filter(driver__user=self.request.user)
        return Vehicle.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return VehicleCreateSerializer
        return VehicleSerializer
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a vehicle (deactivate others)"""
        vehicle = self.get_object()
        
        # Deactivate all other vehicles for this driver
        Vehicle.objects.filter(driver=vehicle.driver).update(is_active=False)
        
        # Activate this vehicle
        vehicle.is_active = True
        vehicle.save()
        
        return Response({'message': 'Vehicle activated successfully'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a vehicle"""
        vehicle = self.get_object()
        vehicle.is_active = False
        vehicle.save()
        
        return Response({'message': 'Vehicle deactivated successfully'})
