from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/ride/(?P<ride_id>[^/]+)/$', consumers.RideConsumer.as_asgi()),
    re_path(r'ws/driver/(?P<driver_id>[^/]+)/$', consumers.DriverConsumer.as_asgi()),
    re_path(r'ws/notifications/(?P<user_id>[^/]+)/$', consumers.NotificationConsumer.as_asgi()),
]
