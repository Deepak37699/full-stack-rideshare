from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Sum, Avg, Count
from decimal import Decimal
import json
import uuid

from .models import Ride, RideRequest
from accounts.models import User
# from accounts.additional_models import Notification, PromoCode, EmergencyContact, SOS
from .services import LocationService, NotificationService


class ChatHistoryView(APIView):
    """API endpoint for ride chat history"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get chat history for rides"""
        try:
            ride_id = request.query_params.get('ride_id')
            
            if not ride_id:
                return Response(
                    {'error': 'Ride ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                ride = Ride.objects.get(id=ride_id)
            except Ride.DoesNotExist:
                return Response(
                    {'error': 'Ride not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verify user is part of this ride
            if request.user not in [ride.rider, ride.driver.user if ride.driver else None]:
                return Response(
                    {'error': 'You are not authorized for this ride'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Mock chat history - in production this would come from a database
            chat_history = [
                {
                    'id': str(uuid.uuid4()),
                    'message': 'I am on my way to pick you up!',
                    'sender': 'driver',
                    'timestamp': (timezone.now() - timezone.timedelta(minutes=5)).isoformat(),
                    'is_read': True
                },
                {
                    'id': str(uuid.uuid4()),
                    'message': 'Thank you! I will be waiting at the main entrance.',
                    'sender': 'rider',
                    'timestamp': (timezone.now() - timezone.timedelta(minutes=3)).isoformat(),
                    'is_read': True
                },
                {
                    'id': str(uuid.uuid4()),
                    'message': 'I am here. Can you see my car?',
                    'sender': 'driver',
                    'timestamp': timezone.now().isoformat(),
                    'is_read': False
                }
            ]
            
            return Response({
                'ride_id': ride_id,
                'messages': chat_history,
                'total_messages': len(chat_history)
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Send a message in ride chat"""
        try:
            ride_id = request.data.get('ride_id')
            message = request.data.get('message', '').strip()
            
            if not ride_id or not message:
                return Response(
                    {'error': 'Ride ID and message are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                ride = Ride.objects.get(id=ride_id)
            except Ride.DoesNotExist:
                return Response(
                    {'error': 'Ride not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verify user is part of this ride
            if request.user not in [ride.rider, ride.driver.user if ride.driver else None]:
                return Response(
                    {'error': 'You are not authorized for this ride'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Create message (mock implementation)
            message_data = {
                'id': str(uuid.uuid4()),
                'message': message,
                'sender': 'driver' if request.user == ride.driver.user else 'rider',
                'timestamp': timezone.now().isoformat(),
                'is_read': False
            }
            
            # In production, save to database and send real-time notification
            print(f"Chat message sent: {message_data}")
            
            return Response(message_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WalletView(APIView):
    """API endpoint for wallet management"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get wallet balance and transaction history"""
        try:
            user = request.user
            
            # Mock wallet data - in production this would come from a payment service
            wallet_data = {
                'balance': 1250.50,
                'currency': 'NPR',
                'transactions': [
                    {
                        'id': str(uuid.uuid4()),
                        'type': 'debit',
                        'amount': 150.00,
                        'description': 'Ride payment - Thamel to Patan',
                        'timestamp': (timezone.now() - timezone.timedelta(hours=2)).isoformat(),
                        'status': 'completed'
                    },
                    {
                        'id': str(uuid.uuid4()),
                        'type': 'credit',
                        'amount': 500.00,
                        'description': 'Wallet top-up via eSewa',
                        'timestamp': (timezone.now() - timezone.timedelta(days=1)).isoformat(),
                        'status': 'completed'
                    },
                    {
                        'id': str(uuid.uuid4()),
                        'type': 'debit',
                        'amount': 200.00,
                        'description': 'Ride payment - Kathmandu to Airport',
                        'timestamp': (timezone.now() - timezone.timedelta(days=2)).isoformat(),
                        'status': 'completed'
                    }
                ],
                'pending_amount': 0.00,
                'available_payment_methods': [
                    'eSewa',
                    'Khalti',
                    'Bank Transfer',
                    'Credit Card'
                ]
            }
            
            return Response(wallet_data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Add money to wallet"""
        try:
            amount = request.data.get('amount')
            payment_method = request.data.get('payment_method')
            
            if not amount or not payment_method:
                return Response(
                    {'error': 'Amount and payment method are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                amount = float(amount)
                if amount <= 0:
                    raise ValueError("Amount must be positive")
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid amount'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mock payment processing
            transaction = {
                'id': str(uuid.uuid4()),
                'amount': amount,
                'payment_method': payment_method,
                'status': 'processing',
                'timestamp': timezone.now().isoformat()
            }
            
            # In production, integrate with actual payment gateway
            print(f"Wallet top-up initiated: {transaction}")
            
            return Response({
                'message': 'Wallet top-up initiated',
                'transaction': transaction
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PromoCodeView(APIView):
    """API endpoint for promo code management"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get available promo codes"""
        try:
            # Mock promo codes - in production, fetch from database
            promo_codes = [
                {
                    'id': str(uuid.uuid4()),
                    'code': 'NEWUSER50',
                    'title': 'New User Discount',
                    'description': 'Get NPR 50 off on your first ride',
                    'discount_type': 'fixed',
                    'discount_value': 50.0,
                    'min_ride_amount': 100.0,
                    'valid_until': (timezone.now() + timezone.timedelta(days=30)).isoformat(),
                    'is_used': False,
                    'usage_limit': 1
                },
                {
                    'id': str(uuid.uuid4()),
                    'code': 'WEEKEND20',
                    'title': 'Weekend Special',
                    'description': 'Get 20% off on weekend rides',
                    'discount_type': 'percentage',
                    'discount_value': 20.0,
                    'min_ride_amount': 200.0,
                    'valid_until': (timezone.now() + timezone.timedelta(days=7)).isoformat(),
                    'is_used': False,
                    'usage_limit': 5
                }
            ]
            
            return Response({
                'available_codes': promo_codes,
                'total_count': len(promo_codes)
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Apply promo code"""
        try:
            promo_code = request.data.get('promo_code', '').strip().upper()
            ride_amount = request.data.get('ride_amount')
            
            if not promo_code:
                return Response(
                    {'error': 'Promo code is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not ride_amount:
                return Response(
                    {'error': 'Ride amount is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                ride_amount = float(ride_amount)
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid ride amount'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mock promo code validation
            valid_codes = {
                'NEWUSER50': {
                    'discount_type': 'fixed',
                    'discount_value': 50.0,
                    'min_ride_amount': 100.0,
                    'max_discount': 50.0
                },
                'WEEKEND20': {
                    'discount_type': 'percentage',
                    'discount_value': 20.0,
                    'min_ride_amount': 200.0,
                    'max_discount': 100.0
                }
            }
            
            if promo_code not in valid_codes:
                return Response(
                    {'error': 'Invalid promo code'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            code_info = valid_codes[promo_code]
            
            if ride_amount < code_info['min_ride_amount']:
                return Response(
                    {'error': f'Minimum ride amount is NPR {code_info["min_ride_amount"]}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculate discount
            if code_info['discount_type'] == 'fixed':
                discount = min(code_info['discount_value'], ride_amount)
            else:  # percentage
                discount = min(
                    (ride_amount * code_info['discount_value'] / 100),
                    code_info['max_discount']
                )
            
            final_amount = ride_amount - discount
            
            return Response({
                'promo_code': promo_code,
                'original_amount': ride_amount,
                'discount_amount': discount,
                'final_amount': final_amount,
                'discount_type': code_info['discount_type'],
                'message': f'Promo code applied! You saved NPR {discount:.2f}'
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReferralView(APIView):
    """API endpoint for referral system"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get referral information"""
        try:
            user = request.user
            
            # Mock referral data
            referral_data = {
                'referral_code': f"REFER{user.id}",
                'total_referrals': 3,
                'successful_referrals': 2,
                'total_earned': 250.0,
                'pending_rewards': 50.0,
                'referral_history': [
                    {
                        'referral_code': f"REFER{user.id}",
                        'referred_user': 'John Doe',
                        'status': 'completed',
                        'reward_amount': 100.0,
                        'date': (timezone.now() - timezone.timedelta(days=5)).isoformat()
                    },
                    {
                        'referral_code': f"REFER{user.id}",
                        'referred_user': 'Jane Smith',
                        'status': 'completed',
                        'reward_amount': 100.0,
                        'date': (timezone.now() - timezone.timedelta(days=10)).isoformat()
                    },
                    {
                        'referral_code': f"REFER{user.id}",
                        'referred_user': 'Bob Wilson',
                        'status': 'pending',
                        'reward_amount': 50.0,
                        'date': (timezone.now() - timezone.timedelta(days=2)).isoformat()
                    }
                ],
                'reward_per_referral': 100.0,
                'terms_and_conditions': [
                    'Referred user must complete their first ride',
                    'Reward will be credited within 24 hours',
                    'Maximum 10 referrals per month',
                    'Referral code expires after 30 days'
                ]
            }
            
            return Response(referral_data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LiveTrackingView(APIView):
    """API endpoint for live driver/ride tracking"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Update live location during ride"""
        try:
            ride_id = request.data.get('ride_id')
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')
            heading = request.data.get('heading', 0)  # Direction in degrees
            speed = request.data.get('speed', 0)  # Speed in km/h
            
            if not all([ride_id, latitude, longitude]):
                return Response(
                    {'error': 'Ride ID, latitude, and longitude are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                ride = Ride.objects.get(id=ride_id)
            except Ride.DoesNotExist:
                return Response(
                    {'error': 'Ride not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verify user is the driver for this ride
            if not ride.driver or request.user != ride.driver.user:
                return Response(
                    {'error': 'You are not authorized to update this ride location'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Update location (in production, this would use Redis or similar for real-time data)
            location_update = {
                'ride_id': ride_id,
                'driver_id': request.user.id,
                'latitude': float(latitude),
                'longitude': float(longitude),
                'heading': float(heading),
                'speed': float(speed),
                'timestamp': timezone.now().isoformat(),
                'estimated_arrival': (timezone.now() + timezone.timedelta(minutes=5)).isoformat()
            }
            
            # In production, broadcast this to the rider via WebSocket
            print(f"Live tracking update: {location_update}")
            
            return Response({
                'message': 'Location updated successfully',
                'tracking_data': location_update
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """Get current ride tracking information"""
        try:
            ride_id = request.query_params.get('ride_id')
            
            if not ride_id:
                return Response(
                    {'error': 'Ride ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                ride = Ride.objects.get(id=ride_id)
            except Ride.DoesNotExist:
                return Response(
                    {'error': 'Ride not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verify user is part of this ride
            if request.user not in [ride.rider, ride.driver.user if ride.driver else None]:
                return Response(
                    {'error': 'You are not authorized for this ride'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Mock tracking data
            tracking_data = {
                'ride_id': ride_id,
                'driver_location': {
                    'latitude': 27.7172,
                    'longitude': 85.3240,
                    'heading': 45,
                    'speed': 25,
                    'last_updated': timezone.now().isoformat()
                },
                'route_progress': {
                    'distance_covered': 2.5,
                    'total_distance': 5.0,
                    'estimated_arrival': (timezone.now() + timezone.timedelta(minutes=8)).isoformat(),
                    'completion_percentage': 50
                },
                'ride_status': ride.status,
                'driver_info': {
                    'name': ride.driver.user.get_full_name() if ride.driver else 'N/A',
                    'phone': ride.driver.user.phone_number if ride.driver else 'N/A',
                    'vehicle_number': ride.driver.vehicle_number if ride.driver else 'N/A',
                    'vehicle_model': ride.driver.vehicle_model if ride.driver else 'N/A'
                }
            }
            
            return Response(tracking_data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NotificationView(APIView):
    """API endpoint for notifications"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user notifications"""
        try:
            user = request.user
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 20))
            
            # Mock notifications
            notifications = [
                {
                    'id': str(uuid.uuid4()),
                    'title': 'Ride Completed',
                    'message': 'Your ride to Patan Durbar Square has been completed',
                    'type': 'ride_completed',
                    'is_read': False,
                    'timestamp': (timezone.now() - timezone.timedelta(minutes=30)).isoformat(),
                    'data': {'ride_id': str(uuid.uuid4())}
                },
                {
                    'id': str(uuid.uuid4()),
                    'title': 'Driver Assigned',
                    'message': 'Ram Sharma is on the way to pick you up',
                    'type': 'driver_assigned',
                    'is_read': True,
                    'timestamp': (timezone.now() - timezone.timedelta(hours=1)).isoformat(),
                    'data': {'ride_id': str(uuid.uuid4()), 'driver_id': '123'}
                },
                {
                    'id': str(uuid.uuid4()),
                    'title': 'Promo Code Available',
                    'message': 'Use code WEEKEND20 for 20% off on your next ride',
                    'type': 'promo_available',
                    'is_read': True,
                    'timestamp': (timezone.now() - timezone.timedelta(hours=4)).isoformat(),
                    'data': {'promo_code': 'WEEKEND20'}
                }
            ]
            
            return Response({
                'notifications': notifications,
                'total_count': len(notifications),
                'unread_count': sum(1 for n in notifications if not n['is_read']),
                'page': page,
                'has_more': False
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def patch(self, request):
        """Mark notifications as read"""
        try:
            notification_ids = request.data.get('notification_ids', [])
            
            if not notification_ids:
                return Response(
                    {'error': 'Notification IDs are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # In production, update notification read status in database
            print(f"Marking notifications as read: {notification_ids}")
            
            return Response({
                'message': f'{len(notification_ids)} notifications marked as read'
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
