from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'rides', views.RideViewSet)
router.register(r'ratings', views.RideRatingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('request-ride/', views.RequestRideView.as_view(), name='request_ride'),
    path('nearby-drivers/', views.NearbyDriversView.as_view(), name='nearby_drivers'),
    path('<uuid:ride_id>/accept/', views.AcceptRideView.as_view(), name='accept_ride'),
    path('<uuid:ride_id>/start/', views.StartRideView.as_view(), name='start_ride'),
    path('<uuid:ride_id>/complete/', views.CompleteRideView.as_view(), name='complete_ride'),
    path('<uuid:ride_id>/cancel/', views.CancelRideView.as_view(), name='cancel_ride'),
    path('<uuid:ride_id>/track/', views.TrackRideView.as_view(), name='track_ride'),
]
