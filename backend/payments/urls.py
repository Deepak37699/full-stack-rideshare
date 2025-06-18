from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'payment-methods', views.PaymentMethodViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'refunds', views.RefundViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('process-payment/', views.ProcessPaymentView.as_view(), name='process_payment'),
    path('add-payment-method/', views.AddPaymentMethodView.as_view(), name='add_payment_method'),
    path('earnings/', views.DriverEarningsListView.as_view(), name='driver_earnings_list'),
]
