from rest_framework import serializers
from .models import Payment, PaymentMethod
from accounts.serializers import UserSerializer
from rides.serializers import RideSerializer

class PaymentMethodSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    last_four_digits = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentMethod
        fields = (
            'id', 'user', 'method_type', 'card_number',
            'cardholder_name', 'expiry_month', 'expiry_year',
            'is_default', 'is_active', 'last_four_digits',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
        extra_kwargs = {
            'card_number': {'write_only': True},
        }
    
    def get_last_four_digits(self, obj):
        if obj.card_number:
            return obj.card_number[-4:] if len(obj.card_number) >= 4 else obj.card_number
        return None
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        
        # If this is set as default, make other payment methods non-default
        if validated_data.get('is_default', False):
            PaymentMethod.objects.filter(
                user=validated_data['user'],
                is_default=True
            ).update(is_default=False)
        
        return super().create(validated_data)

class PaymentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    ride = RideSerializer(read_only=True)
    payment_method = PaymentMethodSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = (
            'id', 'user', 'ride', 'payment_method', 'amount',
            'currency', 'payment_type', 'status', 'transaction_id',
            'gateway_response', 'processed_at', 'failed_at',
            'failure_reason', 'refund_amount', 'refunded_at',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'user', 'transaction_id', 'gateway_response',
            'processed_at', 'failed_at', 'refunded_at',
            'created_at', 'updated_at'
        )

class PaymentProcessSerializer(serializers.Serializer):
    ride_id = serializers.IntegerField()
    payment_method_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='USD')
    
    def validate_ride_id(self, value):
        user = self.context['request'].user
        from rides.models import Ride
        
        try:
            ride = Ride.objects.get(id=value)
            if ride.rider != user:
                raise serializers.ValidationError("You can only pay for your own rides")
            if ride.status != 'completed':
                raise serializers.ValidationError("You can only pay for completed rides")
            
            # Check if payment already exists
            if Payment.objects.filter(ride=ride, status='completed').exists():
                raise serializers.ValidationError("Payment already completed for this ride")
            
            return value
        except Ride.DoesNotExist:
            raise serializers.ValidationError("Ride does not exist")
    
    def validate_payment_method_id(self, value):
        user = self.context['request'].user
        
        try:
            payment_method = PaymentMethod.objects.get(id=value, user=user)
            if not payment_method.is_active:
                raise serializers.ValidationError("Payment method is not active")
            return value
        except PaymentMethod.DoesNotExist:
            raise serializers.ValidationError("Payment method does not exist")

class RefundSerializer(serializers.Serializer):
    payment_id = serializers.IntegerField()
    refund_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    reason = serializers.CharField(max_length=255)
    
    def validate_payment_id(self, value):
        try:
            payment = Payment.objects.get(id=value)
            if payment.status != 'completed':
                raise serializers.ValidationError("Can only refund completed payments")
            if payment.refund_amount and payment.refund_amount > 0:
                raise serializers.ValidationError("Payment already has a refund")
            return value
        except Payment.DoesNotExist:
            raise serializers.ValidationError("Payment does not exist")
    
    def validate_refund_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Refund amount must be greater than 0")
        return value

class PaymentHistorySerializer(serializers.ModelSerializer):
    ride = RideSerializer(read_only=True)
    payment_method = PaymentMethodSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = (
            'id', 'ride', 'payment_method', 'amount', 'currency',
            'payment_type', 'status', 'processed_at', 'failed_at',
            'failure_reason', 'refund_amount', 'refunded_at',
            'created_at'
        )
        read_only_fields = '__all__'

class PaymentSummarySerializer(serializers.Serializer):
    total_spent = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_refunded = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_payments = serializers.IntegerField(read_only=True)
    payment_methods_count = serializers.IntegerField(read_only=True)
