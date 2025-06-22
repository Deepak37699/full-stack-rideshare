from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Ride, RideRequest, RideLocation, FavoriteLocation, RideTemplate, ScheduledRide, SmartSuggestion

@admin.register(RideRequest)
class RideRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'rider', 'pickup_address_short', 'destination_address_short',
        'ride_type', 'estimated_fare', 'status', 'requested_at', 'expires_at'
    )
    list_filter = ('status', 'ride_type', 'requested_at')
    search_fields = ('rider__username', 'rider__email', 'pickup_address', 'destination_address')
    readonly_fields = ('id', 'requested_at', 'expires_at')
    ordering = ('-requested_at',)
    
    fieldsets = (
        ('Request Info', {
            'fields': ('id', 'rider', 'status', 'ride_type')
        }),
        ('Pickup Details', {
            'fields': ('pickup_address', 'pickup_latitude', 'pickup_longitude')
        }),
        ('Destination Details', {
            'fields': ('destination_address', 'destination_latitude', 'destination_longitude')
        }),
        ('Ride Details', {
            'fields': ('estimated_fare', 'distance', 'special_instructions')
        }),
        ('Timestamps', {
            'fields': ('requested_at', 'expires_at')
        })
    )
    
    def pickup_address_short(self, obj):
        return obj.pickup_address[:50] + '...' if len(obj.pickup_address) > 50 else obj.pickup_address
    pickup_address_short.short_description = 'Pickup'
    
    def destination_address_short(self, obj):
        return obj.destination_address[:50] + '...' if len(obj.destination_address) > 50 else obj.destination_address
    destination_address_short.short_description = 'Destination'


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'rider', 'driver', 'pickup_address_short', 'destination_address_short',
        'ride_type', 'fare', 'status', 'requested_at', 'completed_at'
    )
    list_filter = ('status', 'ride_type', 'requested_at', 'completed_at')
    search_fields = (
        'rider__username', 'rider__email', 'driver__user__username',
        'pickup_address', 'destination_address'
    )
    readonly_fields = (
        'id', 'created_at', 'updated_at', 'duration_minutes',
        'view_rider_profile', 'view_driver_profile', 'view_locations'
    )
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Ride Info', {
            'fields': ('id', 'ride_request', 'status', 'ride_type')
        }),
        ('Participants', {
            'fields': ('rider', 'view_rider_profile', 'driver', 'view_driver_profile')
        }),
        ('Pickup Details', {
            'fields': ('pickup_address', 'pickup_latitude', 'pickup_longitude')
        }),
        ('Destination Details', {
            'fields': ('destination_address', 'destination_latitude', 'destination_longitude')
        }),
        ('Ride Details', {
            'fields': ('fare', 'distance', 'duration_minutes')
        }),
        ('Timestamps', {
            'fields': (
                'requested_at', 'accepted_at', 'started_at',
                'completed_at', 'cancelled_at', 'created_at', 'updated_at'
            )
        }),
        ('Ratings & Notes', {
            'fields': (
                'rating_by_rider', 'rating_by_driver',
                'rider_notes', 'driver_notes', 'cancellation_reason'
            )
        }),
        ('Location Tracking', {
            'fields': ('view_locations',)
        })
    )
    
    def pickup_address_short(self, obj):
        return obj.pickup_address[:50] + '...' if len(obj.pickup_address) > 50 else obj.pickup_address
    pickup_address_short.short_description = 'Pickup'
    
    def destination_address_short(self, obj):
        return obj.destination_address[:50] + '...' if len(obj.destination_address) > 50 else obj.destination_address
    destination_address_short.short_description = 'Destination'
    
    def view_rider_profile(self, obj):
        if obj.rider:
            url = reverse('admin:accounts_user_change', args=[obj.rider.id])
            return format_html('<a href="{}" target="_blank">View Profile</a>', url)
        return '-'
    view_rider_profile.short_description = 'Rider Profile'
    
    def view_driver_profile(self, obj):
        if obj.driver:
            url = reverse('admin:drivers_driver_change', args=[obj.driver.id])
            return format_html('<a href="{}" target="_blank">View Profile</a>', url)
        return '-'
    view_driver_profile.short_description = 'Driver Profile'
    
    def view_locations(self, obj):
        count = obj.locations.count()
        if count > 0:
            url = reverse('admin:rides_ridelocation_changelist') + f'?ride__id__exact={obj.id}'
            return format_html('<a href="{}" target="_blank">{} locations</a>', url, count)
        return 'No locations tracked'
    view_locations.short_description = 'Location History'
    
    actions = ['cancel_rides', 'refund_rides']
    
    def cancel_rides(self, request, queryset):
        """Bulk cancel rides"""
        updated = 0
        for ride in queryset:
            if ride.status in ['pending', 'accepted']:
                ride.cancel_ride("Cancelled by admin")
                updated += 1
        
        self.message_user(request, f'{updated} rides cancelled successfully.')
    cancel_rides.short_description = 'Cancel selected rides'
    
    def refund_rides(self, request, queryset):
        """Mark rides for refund"""
        # This would integrate with payment system
        count = queryset.count()
        self.message_user(request, f'{count} rides marked for refund processing.')
    refund_rides.short_description = 'Process refunds for selected rides'


@admin.register(RideLocation)
class RideLocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'ride', 'latitude', 'longitude', 'speed', 'timestamp')
    list_filter = ('timestamp', 'ride__status')
    search_fields = ('ride__id', 'ride__rider__username', 'ride__driver__user__username')
    readonly_fields = ('id', 'timestamp', 'view_on_map')
    ordering = ('-timestamp',)
    
    def view_on_map(self, obj):
        """Generate link to view location on map"""
        if obj.latitude and obj.longitude:
            url = f"https://www.google.com/maps?q={obj.latitude},{obj.longitude}"
            return format_html('<a href="{}" target="_blank">View on Google Maps</a>', url)
        return '-'
    view_on_map.short_description = 'Map View'


# Smart Ride Features Admin
from .models import FavoriteLocation, RideTemplate, ScheduledRide, SmartSuggestion

@admin.register(FavoriteLocation)
class FavoriteLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'location_type', 'address', 'use_count', 'created_at')
    list_filter = ('location_type', 'created_at')
    search_fields = ('name', 'address', 'user__username')
    readonly_fields = ('use_count', 'created_at', 'updated_at')

@admin.register(RideTemplate)  
class RideTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'preferred_ride_type', 'use_count', 'is_active', 'created_at')
    list_filter = ('preferred_ride_type', 'is_active', 'created_at')
    search_fields = ('name', 'user__username', 'pickup_address', 'destination_address')
    readonly_fields = ('use_count', 'last_used', 'created_at')

@admin.register(ScheduledRide)
class ScheduledRideAdmin(admin.ModelAdmin):
    list_display = ('user', 'scheduled_datetime', 'status', 'recurring_pattern', 'ride_type', 'created_at')
    list_filter = ('status', 'recurring_pattern', 'ride_type', 'scheduled_datetime')
    search_fields = ('user__username', 'pickup_address', 'destination_address')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(SmartSuggestion)
class SmartSuggestionAdmin(admin.ModelAdmin):
    list_display = ('user', 'suggestion_type', 'title', 'confidence_score', 'is_active', 'was_used', 'created_at')
    list_filter = ('suggestion_type', 'is_active', 'was_used', 'created_at')
    search_fields = ('user__username', 'title', 'description')
    readonly_fields = ('confidence_score', 'created_at')


# Custom admin views for analytics
class RideAnalyticsAdmin:
    """Custom admin views for ride analytics"""
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Calculate basic statistics
        total_rides = Ride.objects.count()
        completed_rides = Ride.objects.filter(status='completed').count()
        active_rides = Ride.objects.filter(status__in=['accepted', 'in_progress']).count()
        
        # Today's statistics
        today = timezone.now().date()
        today_rides = Ride.objects.filter(created_at__date=today).count()
        
        # Revenue statistics (for completed rides)
        completed_rides_queryset = Ride.objects.filter(status='completed')
        total_revenue = sum(ride.fare for ride in completed_rides_queryset)
        
        extra_context.update({
            'total_rides': total_rides,
            'completed_rides': completed_rides,
            'active_rides': active_rides,
            'today_rides': today_rides,
            'total_revenue': total_revenue,
            'completion_rate': round((completed_rides / total_rides * 100), 2) if total_rides > 0 else 0,
        })
        
        return super().changelist_view(request, extra_context=extra_context)


# Add custom styling for admin
admin.site.site_header = "InDrive Nepal Admin"
admin.site.site_title = "InDrive Nepal"
admin.site.index_title = "Welcome to InDrive Nepal Administration"
