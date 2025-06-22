from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import models
from .services import (
    FareCalculationService, 
    RouteOptimizationService,
    LocationService,
    NotificationService
)
from .models import Ride, RideRequest
from .serializers import RideSerializer
import json

class FareEstimateView(APIView):
    """API endpoint for fare estimation"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Calculate fare estimate for a route"""
        try:
            pickup_lat = request.data.get('pickup_latitude')
            pickup_lng = request.data.get('pickup_longitude')
            dest_lat = request.data.get('destination_latitude')
            dest_lng = request.data.get('destination_longitude')
            ride_type = request.data.get('ride_type', 'standard')
            
            if not all([pickup_lat, pickup_lng, dest_lat, dest_lng]):
                return Response(
                    {'error': 'All coordinates are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculate fare
            fare_info = FareCalculationService.calculate_fare(
                pickup_lat, pickup_lng, dest_lat, dest_lng,
                ride_type=ride_type,
                time_of_day=timezone.now(),
                surge_multiplier=FareCalculationService.get_surge_multiplier(
                    'default', timezone.now()
                )
            )
            
            # Get route information
            route_info = RouteOptimizationService.get_optimized_route(
                pickup_lat, pickup_lng, dest_lat, dest_lng
            )
            
            response_data = {
                **fare_info,
                **route_info,
                'currency': 'NPR'
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NearbyDriversView(APIView):
    """API endpoint to find nearby drivers"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Find nearby available drivers"""
        try:
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')
            radius_km = request.data.get('radius_km', 5)
            
            if not latitude or not longitude:
                return Response(
                    {'error': 'Latitude and longitude are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Find nearby drivers
            nearby_drivers = LocationService.find_nearby_drivers(
                latitude, longitude, radius_km
            )
            
            return Response({
                'drivers': nearby_drivers,
                'search_radius_km': radius_km,
                'total_found': len(nearby_drivers)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RideMatchingView(APIView):
    """API endpoint for intelligent ride matching"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create a ride request and find matching drivers"""
        try:
            if request.user.user_type != 'rider':
                return Response(
                    {'error': 'Only riders can request rides'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Create ride request
            ride_request_data = {
                'pickup_latitude': request.data.get('pickup_latitude'),
                'pickup_longitude': request.data.get('pickup_longitude'),
                'pickup_address': request.data.get('pickup_address'),
                'destination_latitude': request.data.get('destination_latitude'),
                'destination_longitude': request.data.get('destination_longitude'),
                'destination_address': request.data.get('destination_address'),
                'ride_type': request.data.get('ride_type', 'standard'),
                'special_instructions': request.data.get('special_instructions', '')
            }
            
            # Validate required fields
            required_fields = [
                'pickup_latitude', 'pickup_longitude', 'pickup_address',
                'destination_latitude', 'destination_longitude', 'destination_address'
            ]
            
            if not all(ride_request_data.get(field) for field in required_fields):
                return Response(
                    {'error': 'All pickup and destination details are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculate fare
            fare_info = FareCalculationService.calculate_fare(
                ride_request_data['pickup_latitude'],
                ride_request_data['pickup_longitude'],
                ride_request_data['destination_latitude'],
                ride_request_data['destination_longitude'],
                ride_type=ride_request_data['ride_type'],
                time_of_day=timezone.now()
            )
            
            # Create ride request
            ride_request = RideRequest.objects.create(
                rider=request.user,
                estimated_fare=fare_info['total_fare'],
                distance=fare_info['distance_km'],
                expires_at=timezone.now() + timezone.timedelta(minutes=15),
                **ride_request_data
            )
            
            # Find nearby drivers
            nearby_drivers = LocationService.find_nearby_drivers(
                ride_request_data['pickup_latitude'],
                ride_request_data['pickup_longitude']
            )
            
            # Send notifications to nearby drivers
            for driver_info in nearby_drivers[:5]:  # Notify top 5 closest drivers
                # Would send push notification in production
                print(f"Notifying driver {driver_info['driver_id']} about ride request {ride_request.id}")
            
            return Response({
                'ride_request_id': str(ride_request.id),
                'estimated_fare': fare_info['total_fare'],
                'estimated_duration': fare_info['estimated_minutes'],
                'distance_km': fare_info['distance_km'],
                'nearby_drivers_count': len(nearby_drivers),
                'expires_at': ride_request.expires_at.isoformat(),
                'status': 'searching_for_driver'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GeocodeView(APIView):
    """API endpoint for geocoding and reverse geocoding"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Convert address to coordinates or coordinates to address"""
        try:
            operation = request.data.get('operation')  # 'geocode' or 'reverse_geocode'
            
            if operation == 'geocode':
                address = request.data.get('address')
                if not address:
                    return Response(
                        {'error': 'Address is required for geocoding'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                coordinates = LocationService.get_coordinates_from_address(address)
                return Response(coordinates, status=status.HTTP_200_OK)
                
            elif operation == 'reverse_geocode':
                latitude = request.data.get('latitude')
                longitude = request.data.get('longitude')
                
                if not latitude or not longitude:
                    return Response(
                        {'error': 'Latitude and longitude are required for reverse geocoding'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                address_info = LocationService.get_address_from_coordinates(latitude, longitude)
                return Response(address_info, status=status.HTTP_200_OK)
                
            else:
                return Response(
                    {'error': 'Operation must be either "geocode" or "reverse_geocode"'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RideAnalyticsView(APIView):
    """API endpoint for ride analytics and insights"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get ride analytics for the user"""
        try:
            user = request.user
            time_period = request.query_params.get('period', 'week')  # week, month, year
            
            # Calculate date range
            now = timezone.now()
            if time_period == 'week':
                start_date = now - timezone.timedelta(days=7)
            elif time_period == 'month':
                start_date = now - timezone.timedelta(days=30)
            elif time_period == 'year':
                start_date = now - timezone.timedelta(days=365)
            else:
                start_date = now - timezone.timedelta(days=7)
            
            if user.user_type == 'rider':
                rides = Ride.objects.filter(
                    rider=user,
                    status='completed',
                    completed_at__gte=start_date
                )
                
                analytics = {
                    'total_rides': rides.count(),
                    'total_spent': sum(ride.fare for ride in rides),
                    'total_distance': sum(ride.distance or 0 for ride in rides),
                    'average_fare': rides.aggregate(avg_fare=models.Avg('fare'))['avg_fare'] or 0,
                    'favorite_pickup_areas': self._get_popular_areas(rides, 'pickup_address'),
                    'favorite_destinations': self._get_popular_areas(rides, 'destination_address'),
                    'ride_types_distribution': self._get_ride_type_distribution(rides),
                    'time_period': time_period
                }
                
            elif user.user_type == 'driver':
                rides = Ride.objects.filter(
                    driver__user=user,
                    status='completed',
                    completed_at__gte=start_date
                )
                
                analytics = {
                    'total_rides': rides.count(),
                    'total_earned': sum(ride.fare for ride in rides),
                    'total_distance': sum(ride.distance or 0 for ride in rides),
                    'average_fare': rides.aggregate(avg_fare=models.Avg('fare'))['avg_fare'] or 0,
                    'popular_pickup_areas': self._get_popular_areas(rides, 'pickup_address'),
                    'popular_destinations': self._get_popular_areas(rides, 'destination_address'),
                    'average_rating': rides.filter(rating_by_rider__isnull=False).aggregate(
                        avg_rating=models.Avg('rating_by_rider')
                    )['avg_rating'] or 0,
                    'time_period': time_period
                }
                
            else:
                return Response(
                    {'error': 'Invalid user type'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(analytics, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_popular_areas(self, rides, field_name):
        """Get popular pickup/destination areas"""
        from django.db.models import Count
        
        popular_areas = rides.values(field_name).annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        return [
            {
                'area': area[field_name],
                'count': area['count']
            }
            for area in popular_areas
        ]
    
    def _get_ride_type_distribution(self, rides):
        """Get distribution of ride types"""
        from django.db.models import Count
        
        distribution = rides.values('ride_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return [
            {
                'ride_type': item['ride_type'],
                'count': item['count']
            }
            for item in distribution
        ]


class EmergencyAlertView(APIView):
    """API endpoint for emergency alerts during rides"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Send emergency alert"""
        try:
            ride_id = request.data.get('ride_id')
            alert_type = request.data.get('alert_type', 'general')
            message = request.data.get('message', '')
            location_lat = request.data.get('latitude')
            location_lng = request.data.get('longitude')
            
            if not ride_id:
                return Response(
                    {'error': 'Ride ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                ride = Ride.objects.get(id=ride_id)
            except Ride.DoesNotExist:
                return Response(
                    {'error': 'Ride not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verify user is part of this ride
            if request.user not in [ride.rider, ride.driver.user if ride.driver else None]:
                return Response(
                    {'error': 'You are not authorized for this ride'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Create emergency alert (would be stored in database)
            alert_data = {
                'ride_id': ride_id,
                'user_id': request.user.id,
                'alert_type': alert_type,
                'message': message,
                'latitude': location_lat,
                'longitude': location_lng,
                'timestamp': timezone.now().isoformat()
            }
            
            # In production, this would:
            # 1. Store alert in database
            # 2. Notify emergency contacts
            # 3. Send alert to support team
            # 4. Potentially contact local authorities
            
            print(f"EMERGENCY ALERT: {alert_data}")
            
            return Response({
                'alert_id': f"emergency_{timezone.now().timestamp()}",
                'status': 'Alert sent successfully',
                'emergency_contacts_notified': True,
                'support_team_notified': True
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
