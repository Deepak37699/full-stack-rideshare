from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Ride, RideRequest
from .serializers import (
    RideSerializer, RideRequestSerializer, RideUpdateSerializer,
    RideRatingSerializer, RideLocationUpdateSerializer
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
    def rate(self, request, pk=None):
        """Rate a completed ride"""
        ride = self.get_object()
        serializer = RideRatingSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = request.user
            rating = serializer.validated_data['rating']
            review = serializer.validated_data.get('review', '')
            
            if user.user_type == 'rider':
                ride.rating_by_rider = rating
                ride.rider_notes = review
            elif user.user_type == 'driver':
                ride.rating_by_driver = rating
                ride.driver_notes = review
            
            ride.save()
            return Response({'message': 'Rating submitted successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        """Update ride location (driver only)"""
        serializer = RideLocationUpdateSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            ride = self.get_object()
            user = request.user
            
            # Update driver's location
            driver = user.driver_profile
            driver.current_latitude = serializer.validated_data['current_latitude']
            driver.current_longitude = serializer.validated_data['current_longitude']
            driver.last_location_update = timezone.now()
            driver.save()
            
            return Response({'message': 'Location updated successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get ride history for the user"""
        user = request.user
        
        if user.user_type == 'rider':
            rides = Ride.objects.filter(rider=user).order_by('-created_at')
        elif user.user_type == 'driver':
            rides = Ride.objects.filter(driver__user=user).order_by('-created_at')
        else:
            rides = Ride.objects.none()
        
        page = self.paginate_queryset(rides)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(rides, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active ride for the user"""
        user = request.user
        
        if user.user_type == 'rider':
            ride = Ride.objects.filter(
                rider=user,
                status__in=['accepted', 'in_progress']
            ).first()
        elif user.user_type == 'driver':
            ride = Ride.objects.filter(
                driver__user=user,
                status__in=['accepted', 'in_progress']
            ).first()
        else:
            ride = None
        
        if ride:
            return Response(RideSerializer(ride).data)
        else:
            return Response({'message': 'No active ride found'}, status=status.HTTP_404_NOT_FOUND)
