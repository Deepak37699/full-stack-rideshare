from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import PaymentMethod, Payment, Refund, DriverEarnings

# Placeholder view classes - will be implemented later
class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    permission_classes = [IsAuthenticated]

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]

class RefundViewSet(viewsets.ModelViewSet):
    queryset = Refund.objects.all()
    permission_classes = [IsAuthenticated]

class ProcessPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({"message": "Process payment endpoint"}, status=status.HTTP_200_OK)

class AddPaymentMethodView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({"message": "Add payment method endpoint"}, status=status.HTTP_200_OK)

class DriverEarningsListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({"message": "Driver earnings list endpoint"}, status=status.HTTP_200_OK)
