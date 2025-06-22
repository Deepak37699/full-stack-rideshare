from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Avg, Count
from django.utils import timezone
from datetime import timedelta
import json

from .models import Ride, RideRequest, FavoriteLocation, RideTemplate, ScheduledRide, SmartSuggestion
from .serializers import (
    RideSerializer, RideRequestSerializer, RideUpdateSerializer,
    RideRatingSerializer, RideLocationUpdateSerializer,
    FavoriteLocationSerializer, RideTemplateSerializer, ScheduledRideSerializer, SmartSuggestionSerializer
)

class RideRequestViewSet(viewsets.ModelViewSet):
    queryset = RideRequest.objects.all()
    serializer_class = RideRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'rider':
            return RideRequest.objects.filter(rider=user)
        elif user.user_type == 'driver':
            # Drivers can see available ride requests
            return RideRequest.objects.filter(
                status='pending',
                expires_at__gt=timezone.now()
            )
        return RideRequest.objects.none()
    
    def perform_create(self, serializer):
        # Set expiry time (15 minutes from now)
        expires_at = timezone.now() + timedelta(minutes=15)
        serializer.save(rider=self.request.user, expires_at=expires_at)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Driver accepts a ride request"""
        if request.user.user_type != 'driver':
            return Response(
                {'error': 'Only drivers can accept ride requests'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            ride_request = self.get_object()
            driver = request.user.driver_profile
            
            if not driver.is_available:
                return Response(
                    {'error': 'Driver is not available'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if ride_request.status != 'pending':
                return Response(
                    {'error': 'Ride request is no longer available'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create ride from ride request
            ride = Ride.objects.create(
                ride_request=ride_request,
                rider=ride_request.rider,
                driver=driver,
                pickup_latitude=ride_request.pickup_latitude,
                pickup_longitude=ride_request.pickup_longitude,
                pickup_address=ride_request.pickup_address,
                destination_latitude=ride_request.destination_latitude,
                destination_longitude=ride_request.destination_longitude,
                destination_address=ride_request.destination_address,
                ride_type=ride_request.ride_type,
                fare=ride_request.estimated_fare,
                distance=ride_request.distance,
                status='accepted'
            )
            
            # Update ride request status
            ride_request.status = 'accepted'
            ride_request.save()
            
            # Set driver as unavailable
            driver.is_available = False
            driver.save()
            
            return Response(RideSerializer(ride).data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'rider':
            return Ride.objects.filter(rider=user)
        elif user.user_type == 'driver':
            return Ride.objects.filter(driver__user=user)
        return Ride.objects.none()
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Driver starts the ride"""
        ride = self.get_object()
        if request.user.user_type != 'driver' or ride.driver.user != request.user:
            return Response(
                {'error': 'Only the assigned driver can start the ride'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if ride.status != 'accepted':
            return Response(
                {'error': 'Ride cannot be started'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ride.status = 'in_progress'
        ride.started_at = timezone.now()
        ride.save()
        
        return Response(RideSerializer(ride).data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Driver completes the ride"""
        ride = self.get_object()
        if request.user.user_type != 'driver' or ride.driver.user != request.user:
            return Response(
                {'error': 'Only the assigned driver can complete the ride'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if ride.status != 'in_progress':
            return Response(
                {'error': 'Ride cannot be completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ride.status = 'completed'
        ride.completed_at = timezone.now()
        ride.save()
        
        # Make driver available again
        ride.driver.is_available = True
        ride.driver.save()
        
        return Response(RideSerializer(ride).data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a ride"""
        ride = self.get_object()
        user = request.user
        
        # Both rider and driver can cancel
        if user.user_type == 'rider' and ride.rider != user:
            return Response(
                {'error': 'You can only cancel your own rides'},
                status=status.HTTP_403_FORBIDDEN
            )
        elif user.user_type == 'driver' and ride.driver.user != user:
            return Response(
                {'error': 'You can only cancel rides assigned to you'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if ride.status in ['completed', 'cancelled']:
            return Response(
                {'error': 'Ride cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = RideUpdateSerializer(ride, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            ride.status = 'cancelled'
            ride.cancelled_at = timezone.now()
            ride.cancellation_reason = serializer.validated_data.get('cancellation_reason', '')
            ride.save()
            
            # Make driver available again if assigned
            if ride.driver:
                ride.driver.is_available = True
                ride.driver.save()
            
            return Response(RideSerializer(ride).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        """Update real-time location during ride"""
        ride = self.get_object()
        
        if request.user.user_type != 'driver' or ride.driver.user != request.user:
            return Response(
                {'error': 'Only the assigned driver can update location'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if ride.status not in ['accepted', 'in_progress']:
            return Response(
                {'error': 'Cannot update location for this ride status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        speed = request.data.get('speed')
        
        if not latitude or not longitude:
            return Response(
                {'error': 'Latitude and longitude are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create location record
        from .models import RideLocation
        location = RideLocation.objects.create(
            ride=ride,
            latitude=latitude,
            longitude=longitude,
            speed=speed
        )
          # Send real-time update to riders (would use WebSocket in production)
        print(f"Location update for ride {ride.id}: {latitude}, {longitude}")
        
        return Response({'status': 'Location updated successfully'})

    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Rate the ride (rider or driver)"""
        ride = self.get_object()
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')
        
        if not rating or not (1 <= int(rating) <= 5):
            return Response(
                {'error': 'Rating must be between 1 and 5'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if ride.status != 'completed':
            return Response(
                {'error': 'Can only rate completed rides'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.user == ride.rider:
            if ride.rating_by_rider:
                return Response(
                    {'error': 'You have already rated this ride'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ride.rating_by_rider = rating
            ride.rider_notes = comment
        elif request.user == ride.driver.user:
            if ride.rating_by_driver:
                return Response(
                    {'error': 'You have already rated this ride'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ride.rating_by_driver = rating
            ride.driver_notes = comment
        else:
            return Response(
                {'error': 'You are not authorized to rate this ride'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        ride.save()
        return Response(RideSerializer(ride).data)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active ride for the user"""
        user = request.user
        
        if user.user_type == 'rider':
            active_ride = Ride.objects.filter(
                rider=user,
                status__in=['accepted', 'in_progress']
            ).first()
        elif user.user_type == 'driver':
            active_ride = Ride.objects.filter(
                driver__user=user,
                status__in=['accepted', 'in_progress']
            ).first()
        else:
            return Response(
                {'error': 'Invalid user type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if active_ride:
            return Response(RideSerializer(active_ride).data)
        else:
            return Response({'message': 'No active ride found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get ride history with pagination and filters"""
        user = request.user
        
        if user.user_type == 'rider':
            queryset = Ride.objects.filter(rider=user, status='completed')
        elif user.user_type == 'driver':
            queryset = Ride.objects.filter(driver__user=user, status='completed')
        else:
            return Response(
                {'error': 'Invalid user type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Apply filters
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        ride_type = request.query_params.get('ride_type')
        
        if date_from:
            queryset = queryset.filter(completed_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(completed_at__date__lte=date_to)
        if ride_type:
            queryset = queryset.filter(ride_type=ride_type)
        
        # Pagination
        page_size = int(request.query_params.get('page_size', 10))
        page = int(request.query_params.get('page', 1))
        
        start = (page - 1) * page_size
        end = start + page_size
        
        rides = queryset[start:end]
        total_count = queryset.count()
        
        return Response({
            'rides': RideSerializer(rides, many=True).data,
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'has_next': end < total_count
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get ride statistics for the user"""
        user = request.user
        
        if user.user_type == 'rider':
            rides = Ride.objects.filter(rider=user, status='completed')
            stats = {
                'total_rides': rides.count(),
                'total_spent': sum(ride.fare for ride in rides),
                'average_rating_given': rides.filter(rating_by_rider__isnull=False).aggregate(
                    avg=Avg('rating_by_rider')
                )['avg'] or 0,
                'favorite_destinations': rides.values('destination_address').annotate(
                    count=Count('id')
                ).order_by('-count')[:5]
            }
        elif user.user_type == 'driver':
            rides = Ride.objects.filter(driver__user=user, status='completed')
            stats = {
                'total_rides': rides.count(),
                'total_earned': sum(ride.fare for ride in rides),
                'average_rating': rides.filter(rating_by_driver__isnull=False).aggregate(
                    avg=Avg('rating_by_driver')
                )['avg'] or 0,
                'total_distance': sum(ride.distance or 0 for ride in rides),
                'acceptance_rate': 85,  # This would need more complex calculation
            }
        else:
            return Response(
                {'error': 'Invalid user type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(stats)

# Smart Ride Features ViewSets

class FavoriteLocationViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteLocationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FavoriteLocation.objects.filter(
            user=self.request.user
        ).order_by('location_type', 'name')
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get favorite locations grouped by type"""
        locations = self.get_queryset()
        grouped = {}
        for location in locations:
            loc_type = location.location_type
            if loc_type not in grouped:
                grouped[loc_type] = []
            grouped[loc_type].append(FavoriteLocationSerializer(location).data)
        return Response(grouped)


class RideTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = RideTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return RideTemplate.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-use_count', 'name')
    
    @action(detail=True, methods=['post'])
    def use_template(self, request, pk=None):
        """Create a ride request from a template"""
        template = self.get_object()
        
        # Create ride request data from template
        ride_data = {
            'pickup_address': template.pickup_address,
            'pickup_latitude': template.pickup_latitude,
            'pickup_longitude': template.pickup_longitude,
            'destination_address': template.destination_address,
            'destination_latitude': template.destination_latitude,
            'destination_longitude': template.destination_longitude,
            'ride_type': template.preferred_ride_type,
            'special_instructions': template.special_instructions,
        }
        
        # Create ride request
        serializer = RideRequestSerializer(data=ride_data, context={'request': request})
        if serializer.is_valid():
            ride_request = serializer.save()
            
            # Update template usage count
            template.use_count += 1
            template.save()
            
            return Response(RideRequestSerializer(ride_request).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScheduledRideViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduledRideSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ScheduledRide.objects.filter(
            user=self.request.user
        ).order_by('scheduled_datetime')
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming scheduled rides"""
        upcoming_rides = self.get_queryset().filter(
            scheduled_datetime__gt=timezone.now(),
            status__in=['scheduled', 'confirmed']
        )
        serializer = ScheduledRideSerializer(upcoming_rides, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def due_for_booking(self, request):
        """Get rides that are due for booking now"""
        due_rides = []
        for ride in self.get_queryset().filter(status='scheduled'):
            if ride.is_due_for_booking():
                due_rides.append(ride)
        
        serializer = ScheduledRideSerializer(due_rides, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def book_now(self, request, pk=None):
        """Immediately book a scheduled ride"""
        scheduled_ride = self.get_object()
        
        if scheduled_ride.status != 'scheduled':
            return Response(
                {'error': 'Ride is not in scheduled status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create ride request from scheduled ride
        ride_data = {
            'pickup_address': scheduled_ride.pickup_address,
            'pickup_latitude': scheduled_ride.pickup_latitude,
            'pickup_longitude': scheduled_ride.pickup_longitude,
            'destination_address': scheduled_ride.destination_address,
            'destination_latitude': scheduled_ride.destination_latitude,
            'destination_longitude': scheduled_ride.destination_longitude,
            'ride_type': scheduled_ride.ride_type,
            'special_instructions': scheduled_ride.special_instructions,
        }
        
        serializer = RideRequestSerializer(data=ride_data, context={'request': request})
        if serializer.is_valid():
            ride_request = serializer.save()
            
            # Update scheduled ride status
            scheduled_ride.status = 'confirmed'
            scheduled_ride.save()
            
            return Response(RideRequestSerializer(ride_request).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SmartSuggestionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SmartSuggestionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SmartSuggestion.objects.filter(
            user=self.request.user,
            is_active=True,
            expires_at__gt=timezone.now()
        ).order_by('-confidence_score', '-created_at')
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get suggestions grouped by type"""
        suggestion_type = request.query_params.get('type', None)
        suggestions = self.get_queryset()
        
        if suggestion_type:
            suggestions = suggestions.filter(suggestion_type=suggestion_type)
        
        grouped = {}
        for suggestion in suggestions:
            stype = suggestion.suggestion_type
            if stype not in grouped:
                grouped[stype] = []
            grouped[stype].append(SmartSuggestionSerializer(suggestion).data)        
        return Response(grouped)
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss a suggestion"""
        suggestion = self.get_object()
        suggestion.is_active = False
        suggestion.save()
        return Response({'status': 'dismissed'})
    
    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """Mark a suggestion as used and optionally create a ride request"""
        suggestion = self.get_object()
        suggestion.was_used = True
        suggestion.save()
        
        # If suggestion has location data, create a ride request
        if (suggestion.suggested_pickup_lat and suggestion.suggested_pickup_lng and
            suggestion.suggested_destination_lat and suggestion.suggested_destination_lng):
            
            ride_data = {
                'pickup_address': suggestion.suggested_pickup_address or 'Suggested Location',
                'pickup_latitude': suggestion.suggested_pickup_lat,
                'pickup_longitude': suggestion.suggested_pickup_lng,
                'destination_address': suggestion.suggested_destination_address or 'Suggested Destination',
                'destination_latitude': suggestion.suggested_destination_lat,
                'destination_longitude': suggestion.suggested_destination_lng,
                'ride_type': 'standard',
            }
            
            serializer = RideRequestSerializer(data=ride_data, context={'request': request})
            if serializer.is_valid():
                ride_request = serializer.save()
                return Response({
                    'status': 'used',
                    'ride_request': RideRequestSerializer(ride_request).data
                }, status=status.HTTP_201_CREATED)
        
        return Response({'status': 'used'})
