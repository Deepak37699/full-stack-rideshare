from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from django.utils import timezone
from .models import Payment, PaymentMethod
from .serializers import (
    PaymentSerializer, PaymentMethodSerializer, PaymentProcessSerializer,
    RefundSerializer, PaymentHistorySerializer, PaymentSummarySerializer
)

class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user, is_active=True)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set a payment method as default"""
        payment_method = self.get_object()
        
        # Remove default from all other payment methods
        PaymentMethod.objects.filter(
            user=request.user,
            is_default=True
        ).update(is_default=False)
        
        # Set this one as default
        payment_method.is_default = True
        payment_method.save()
        
        return Response({'message': 'Payment method set as default'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a payment method"""
        payment_method = self.get_object()
        payment_method.is_active = False
        payment_method.save()
        
        return Response({'message': 'Payment method deactivated'})

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def process_payment(self, request):
        """Process payment for a ride"""
        serializer = PaymentProcessSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            # Get validated data
            ride_id = serializer.validated_data['ride_id']
            payment_method_id = serializer.validated_data['payment_method_id']
            amount = serializer.validated_data['amount']
            currency = serializer.validated_data['currency']
            
            from rides.models import Ride
            ride = Ride.objects.get(id=ride_id)
            payment_method = PaymentMethod.objects.get(id=payment_method_id)
            
            try:
                # Create payment record
                payment = Payment.objects.create(
                    user=request.user,
                    ride=ride,
                    payment_method=payment_method,
                    amount=amount,
                    currency=currency,
                    payment_type='ride_fare',
                    status='pending'
                )
                
                # Process payment with gateway (mock implementation)
                payment_success = self._process_with_gateway(payment)
                
                if payment_success:
                    payment.status = 'completed'
                    payment.processed_at = timezone.now()
                    payment.transaction_id = f"txn_{payment.id}_{timezone.now().timestamp()}"
                    
                    # Update driver earnings
                    ride.driver.total_earnings += amount
                    ride.driver.save()
                else:
                    payment.status = 'failed'
                    payment.failed_at = timezone.now()
                    payment.failure_reason = 'Payment gateway error'
                
                payment.save()
                
                return Response({
                    'payment': PaymentSerializer(payment).data,
                    'message': 'Payment processed successfully' if payment_success else 'Payment failed'
                }, status=status.HTTP_201_CREATED if payment_success else status.HTTP_400_BAD_REQUEST)
                
            except Exception as e:
                return Response(
                    {'error': f'Payment processing failed: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _process_with_gateway(self, payment):
        """Mock payment gateway processing"""
        # In a real implementation, this would integrate with Stripe, PayPal, etc.
        import random
        return random.choice([True, True, True, False])  # 75% success rate for demo
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Process a refund for a payment"""
        payment = self.get_object()
        serializer = RefundSerializer(data=request.data)
        
        if serializer.is_valid():
            refund_amount = serializer.validated_data['refund_amount']
            reason = serializer.validated_data['reason']
            
            if refund_amount > payment.amount:
                return Response(
                    {'error': 'Refund amount cannot exceed payment amount'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                # Process refund (mock implementation)
                refund_success = True  # Mock success
                
                if refund_success:
                    payment.refund_amount = refund_amount
                    payment.refunded_at = timezone.now()
                    payment.save()
                    
                    # Update driver earnings
                    if payment.ride and payment.ride.driver:
                        payment.ride.driver.total_earnings -= refund_amount
                        payment.ride.driver.save()
                    
                    return Response({
                        'message': 'Refund processed successfully',
                        'refund_amount': refund_amount
                    })
                else:
                    return Response(
                        {'error': 'Refund processing failed'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
            except Exception as e:
                return Response(
                    {'error': f'Refund processing failed: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get payment history for the user"""
        payments = self.get_queryset()
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            payments = payments.filter(status=status_filter)
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            payments = payments.filter(created_at__date__gte=start_date)
        if end_date:
            payments = payments.filter(created_at__date__lte=end_date)
        
        page = self.paginate_queryset(payments)
        if page is not None:
            serializer = PaymentHistorySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PaymentHistorySerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get payment summary for the user"""
        payments = Payment.objects.filter(user=request.user)
        
        summary_data = {
            'total_spent': payments.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0,
            'total_refunded': payments.filter(refund_amount__gt=0).aggregate(Sum('refund_amount'))['refund_amount__sum'] or 0,
            'total_payments': payments.filter(status='completed').count(),
            'payment_methods_count': PaymentMethod.objects.filter(user=request.user, is_active=True).count(),
        }
        
        serializer = PaymentSummarySerializer(summary_data)
        return Response(serializer.data)
