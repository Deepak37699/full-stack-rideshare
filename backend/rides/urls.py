from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'rides', views.RideViewSet)
router.register(r'requests', views.RideRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
