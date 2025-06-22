from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal
import json
import math

class FareCalculationService:
    """Service for calculating ride fares based on distance, time, and demand"""
    
    BASE_FARE = Decimal('50.00')  # Base fare in NPR
    RATE_PER_KM = Decimal('15.00')  # Rate per kilometer
    RATE_PER_MINUTE = Decimal('2.00')  # Rate per minute
    
    RIDE_TYPE_MULTIPLIERS = {
        'standard': Decimal('1.0'),
        'premium': Decimal('1.5'),
        'luxury': Decimal('2.0'),
        'shared': Decimal('0.7'),
    }
    
    @classmethod
    def calculate_fare(cls, pickup_lat, pickup_lng, dest_lat, dest_lng, 
                      ride_type='standard', time_of_day=None, surge_multiplier=1.0):
        """Calculate fare based on distance and other factors"""
        
        # Calculate distance
        distance_km = cls.calculate_distance(pickup_lat, pickup_lng, dest_lat, dest_lng)
        
        # Base calculation
        base_fare = cls.BASE_FARE
        distance_fare = distance_km * cls.RATE_PER_KM
        
        # Estimated time (rough calculation)
        estimated_minutes = distance_km * 3  # Assuming 20 km/h average speed
        time_fare = estimated_minutes * cls.RATE_PER_MINUTE
        
        # Total before multipliers
        subtotal = base_fare + distance_fare + time_fare
        
        # Apply ride type multiplier
        ride_multiplier = cls.RIDE_TYPE_MULTIPLIERS.get(ride_type, Decimal('1.0'))
        subtotal *= ride_multiplier
        
        # Apply surge pricing
        if surge_multiplier > 1.0:
            subtotal *= Decimal(str(surge_multiplier))
          # Apply time-based pricing
        if time_of_day:
            time_multiplier = cls.get_time_multiplier(time_of_day)
            subtotal *= time_multiplier
        
        return {
            'base_fare': float(base_fare),
            'distance_fare': float(distance_fare),
            'time_fare': float(time_fare),
            'distance_km': float(distance_km),
            'estimated_minutes': float(estimated_minutes),
            'ride_type_multiplier': float(ride_multiplier),
            'surge_multiplier': surge_multiplier,
            'total_fare': float(subtotal)
        }
    
    @classmethod
    def calculate_distance(cls, lat1, lng1, lat2, lng2):
        """Calculate distance between two points using Haversine formula"""
        # Convert latitude and longitude from degrees to radians
        lat1, lng1, lat2, lng2 = map(math.radians, [float(lat1), float(lng1), float(lat2), float(lng2)])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        distance = c * r
        
        return Decimal(str(round(distance, 2)))
    
    @classmethod
    def get_time_multiplier(cls, time_of_day):
        """Get pricing multiplier based on time of day"""
        hour = time_of_day.hour
        
        # Peak hours (7-9 AM, 5-8 PM)
        if (7 <= hour <= 9) or (17 <= hour <= 20):
            return Decimal('1.3')
        # Late night (10 PM - 5 AM)
        elif hour >= 22 or hour <= 5:
            return Decimal('1.2')
        # Regular hours
        else:
            return Decimal('1.0')
    
    @classmethod
    def get_surge_multiplier(cls, area_code, current_time):
        """Calculate surge pricing based on demand in area"""
        # This would typically connect to a real-time demand monitoring system
        # For now, return a simple calculation
        
        from django.utils import timezone
        from .models import Ride
        
        # Count active rides in the area in the last hour
        one_hour_ago = current_time - timezone.timedelta(hours=1)
        
        active_rides_count = Ride.objects.filter(
            status__in=['accepted', 'in_progress'],
            requested_at__gte=one_hour_ago
        ).count()
        
        # Simple surge calculation
        if active_rides_count > 20:
            return 2.0
        elif active_rides_count > 10:
            return 1.5
        elif active_rides_count > 5:
            return 1.2
        else:
            return 1.0


class RouteOptimizationService:
    """Service for route optimization and ETA calculation"""
    
    @classmethod
    def get_optimized_route(cls, pickup_lat, pickup_lng, dest_lat, dest_lng):
        """Get optimized route using Google Maps API (or similar)"""
        
        # For demo purposes, return a simple calculation
        # In production, this would use Google Maps Directions API
        
        distance = FareCalculationService.calculate_distance(
            pickup_lat, pickup_lng, dest_lat, dest_lng
        )
        
        # Estimate travel time (assuming 25 km/h average in city)
        estimated_minutes = float(distance) * 2.4
        
        return {
            'distance_km': float(distance),
            'estimated_duration_minutes': round(estimated_minutes),
            'route_points': [
                {'lat': float(pickup_lat), 'lng': float(pickup_lng)},
                {'lat': float(dest_lat), 'lng': float(dest_lng)}
            ],
            'instructions': [
                f"Head towards destination",
                f"Continue for {float(distance):.1f} km",
                f"Arrive at destination"
            ]
        }
    
    @classmethod
    def calculate_eta(cls, driver_lat, driver_lng, pickup_lat, pickup_lng):
        """Calculate ETA for driver to reach pickup location"""
        
        distance = FareCalculationService.calculate_distance(
            driver_lat, driver_lng, pickup_lat, pickup_lng
        )
        
        # Assume faster speed for driver going to pickup (30 km/h)
        eta_minutes = float(distance) * 2
        
        return {
            'distance_to_pickup_km': float(distance),
            'eta_minutes': round(eta_minutes),
            'eta_text': f"{round(eta_minutes)} minutes away"
        }


class LocationService:
    """Service for location-based operations"""
    
    @classmethod
    def get_address_from_coordinates(cls, latitude, longitude):
        """Get address from coordinates using reverse geocoding"""
        
        # This would use Google Maps Geocoding API or similar
        # For demo, return a formatted address
        
        return {
            'formatted_address': f"Location near {latitude:.4f}, {longitude:.4f}, Kathmandu, Nepal",
            'locality': 'Kathmandu',
            'area': 'Central Kathmandu',
            'postal_code': '44600',
            'country': 'Nepal'
        }
    
    @classmethod
    def get_coordinates_from_address(cls, address):
        """Get coordinates from address using geocoding"""
        
        # This would use Google Maps Geocoding API
        # For demo, return default Kathmandu coordinates
        
        return {
            'latitude': 27.7172,
            'longitude': 85.3240,
            'accuracy': 'high'
        }
    
    @classmethod
    def find_nearby_drivers(cls, latitude, longitude, radius_km=5):
        """Find drivers within specified radius"""
        
        from drivers.models import Driver
        from django.db.models import Q
        
        # This is a simplified version
        # In production, you'd use spatial queries or external services
        
        available_drivers = Driver.objects.filter(
            is_available=True,
            user__is_active=True
        )
        
        nearby_drivers = []
        for driver in available_drivers:
            if driver.current_latitude and driver.current_longitude:
                distance = FareCalculationService.calculate_distance(
                    latitude, longitude,
                    driver.current_latitude, driver.current_longitude
                )
                
                if distance <= radius_km:
                    eta_info = RouteOptimizationService.calculate_eta(
                        driver.current_latitude, driver.current_longitude,
                        latitude, longitude
                    )
                    
                    nearby_drivers.append({
                        'driver_id': driver.id,
                        'driver_name': driver.user.get_full_name(),
                        'vehicle_info': f"{driver.vehicle_make} {driver.vehicle_model}",
                        'distance_km': float(distance),
                        'eta_minutes': eta_info['eta_minutes'],
                        'rating': float(driver.average_rating or 5.0),
                        'latitude': float(driver.current_latitude),
                        'longitude': float(driver.current_longitude)
                    })
        
        # Sort by distance
        nearby_drivers.sort(key=lambda x: x['distance_km'])
        
        return nearby_drivers


class NotificationService:
    """Service for sending notifications to users"""
    
    @classmethod
    def send_ride_notification(cls, user, notification_type, ride_data):
        """Send ride-related notifications"""
        
        # Create notification data
        notification = {
            'type': 'ride_notification',
            'notification_type': notification_type,
            'data': ride_data,
            'timestamp': timezone.now().isoformat()
        }
        
        try:
            # Would use channels for real-time notifications
            # For now, just log the notification
            print(f"Notification sent to user {user.id}: {notification}")
        except Exception as e:
            print(f"Error sending notification: {e}")
    
    @classmethod
    def send_driver_match_notification(cls, rider, driver, ride):
        """Send notification when driver is matched"""
        
        cls.send_ride_notification(
            rider,
            'driver_matched',
            {
                'ride_id': str(ride.id),
                'driver_name': driver.user.get_full_name(),
                'vehicle_info': f"{driver.vehicle_make} {driver.vehicle_model}",
                'driver_phone': driver.user.phone_number,
                'estimated_arrival': 5  # minutes
            }
        )
    
    @classmethod
    def send_ride_status_update(cls, user, ride, status):
        """Send ride status update notifications"""
        
        status_messages = {
            'accepted': 'Your ride has been accepted by a driver',
            'in_progress': 'Your ride has started',
            'completed': 'Your ride has been completed',
            'cancelled': 'Your ride has been cancelled'
        }
        
        cls.send_ride_notification(
            user,
            'status_update',
            {
                'ride_id': str(ride.id),
                'status': status,
                'message': status_messages.get(status, 'Ride status updated')
            }
        )
