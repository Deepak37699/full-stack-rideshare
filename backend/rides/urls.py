from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views
from . import advanced_api_views
from . import admin_api_views

router = DefaultRouter()
router.register(r'rides', views.RideViewSet)
router.register(r'requests', views.RideRequestViewSet)

# Smart Ride Features
router.register(r'favorite-locations', views.FavoriteLocationViewSet, basename='favoritelocation')
router.register(r'ride-templates', views.RideTemplateViewSet, basename='ridetemplate')
router.register(r'scheduled-rides', views.ScheduledRideViewSet, basename='scheduledride')
router.register(r'smart-suggestions', views.SmartSuggestionViewSet, basename='smartsuggestion')

urlpatterns = [
    path('', include(router.urls)),

    # Enhanced API endpoints
    path('fare-estimate/', api_views.FareEstimateView.as_view(), name='fare-estimate'),
    path('nearby-drivers/', api_views.NearbyDriversView.as_view(), name='nearby-drivers'),
    path('match-ride/', api_views.RideMatchingView.as_view(), name='match-ride'),
    path('geocode/', api_views.GeocodeView.as_view(), name='geocode'),
    path('analytics/', api_views.RideAnalyticsView.as_view(), name='analytics'),
    path('emergency-alert/', api_views.EmergencyAlertView.as_view(), name='emergency-alert'),
    
    # Advanced feature endpoints
    path('chat-history/', advanced_api_views.ChatHistoryView.as_view(), name='chat-history'),
    path('wallet/', advanced_api_views.WalletView.as_view(), name='wallet'),
    path('promo-codes/', advanced_api_views.PromoCodeView.as_view(), name='promo-codes'),
    path('referrals/', advanced_api_views.ReferralView.as_view(), name='referrals'),
    path('live-tracking/', advanced_api_views.LiveTrackingView.as_view(), name='live-tracking'),
    path('notifications/', advanced_api_views.NotificationView.as_view(), name='notifications'),
    
    # Admin dashboard endpoints
    path('admin/dashboard/', admin_api_views.AdminDashboardView.as_view(), name='admin-dashboard'),
    path('admin/health/', admin_api_views.SystemHealthView.as_view(), name='system-health'),
    path('admin/business-analytics/', admin_api_views.BusinessAnalyticsView.as_view(), name='business-analytics'),
]
