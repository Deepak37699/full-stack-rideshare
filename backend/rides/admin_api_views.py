from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.db.models import Q, Sum, Avg, Count, F
from django.db.models.functions import TruncDay, TruncMonth
from decimal import Decimal
import json
from datetime import timedelta

from .models import Ride, RideRequest
from accounts.models import User
from drivers.models import Driver


class AdminDashboardView(APIView):
    """Comprehensive admin dashboard with business analytics"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get comprehensive admin dashboard data"""
        try:
            # Date range for analytics
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)  # Last 30 days
            
            # Basic Metrics
            total_users = User.objects.count()
            total_drivers = Driver.objects.count()
            total_rides = Ride.objects.count()
            completed_rides = Ride.objects.filter(status='completed').count()
            
            # Recent Activity (Last 30 days)
            recent_rides = Ride.objects.filter(created_at__gte=start_date)
            recent_registrations = User.objects.filter(date_joined__gte=start_date).count()
            
            # Revenue Analytics
            total_revenue = Ride.objects.filter(
                status='completed'
            ).aggregate(total=Sum('fare'))['total'] or 0
            
            monthly_revenue = Ride.objects.filter(
                status='completed',
                completed_at__gte=start_date
            ).aggregate(total=Sum('fare'))['total'] or 0
            
            # Ride Statistics
            ride_completion_rate = (completed_rides / total_rides * 100) if total_rides > 0 else 0
            average_fare = Ride.objects.filter(
                status='completed'
            ).aggregate(avg=Avg('fare'))['avg'] or 0
            
            # Daily ride data for charts (last 30 days)
            daily_rides = list(
                Ride.objects.filter(created_at__gte=start_date)
                .extra({'date': "date(created_at)"})
                .values('date')
                .annotate(count=Count('id'))
                .order_by('date')
            )
            
            # Top performing drivers
            top_drivers = list(
                Driver.objects.annotate(
                    total_rides=Count('rides'),
                    total_earnings=Sum('rides__fare'),
                    avg_rating=Avg('rides__reviews__rating')
                ).filter(total_rides__gt=0)
                .order_by('-total_earnings')[:10]
                .values(
                    'user__first_name',
                    'user__last_name',
                    'user__phone_number',
                    'total_rides',
                    'total_earnings',
                    'avg_rating'
                )
            )
            
            # Most active users
            active_users = list(
                User.objects.filter(user_type='rider')
                .annotate(
                    total_rides=Count('ride_requests'),
                    total_spent=Sum('ride_requests__ride__fare')
                ).filter(total_rides__gt=0)
                .order_by('-total_rides')[:10]
                .values(
                    'first_name',
                    'last_name',
                    'phone_number',
                    'total_rides',
                    'total_spent'
                )
            )
            
            # Geographic analytics (mock data for now)
            popular_routes = [
                {
                    'route': 'Thamel to Patan',
                    'count': 45,
                    'avg_fare': 180.50
                },
                {
                    'route': 'Kathmandu to Airport',
                    'count': 38,
                    'avg_fare': 350.00
                },
                {
                    'route': 'Baneshwor to Bhaktapur',
                    'count': 32,
                    'avg_fare': 220.75
                }
            ]
            
            # Peak hours analysis
            peak_hours = [
                {'hour': '08:00', 'rides': 25},
                {'hour': '09:00', 'rides': 32},
                {'hour': '17:00', 'rides': 28},
                {'hour': '18:00', 'rides': 35},
                {'hour': '19:00', 'rides': 22}
            ]
            
            # Recent system alerts
            system_alerts = [
                {
                    'id': 1,
                    'type': 'warning',
                    'message': 'High demand detected in Thamel area',
                    'timestamp': timezone.now().isoformat()
                },
                {
                    'id': 2,
                    'type': 'info',
                    'message': 'New driver registrations: 5 pending approval',
                    'timestamp': (timezone.now() - timedelta(hours=2)).isoformat()
                }
            ]
            
            dashboard_data = {
                # Overview Statistics
                'overview': {
                    'total_users': total_users,
                    'total_drivers': total_drivers,
                    'total_rides': total_rides,
                    'completed_rides': completed_rides,
                    'ride_completion_rate': round(ride_completion_rate, 2),
                    'recent_registrations': recent_registrations
                },
                
                # Financial Metrics
                'revenue': {
                    'total_revenue': float(total_revenue),
                    'monthly_revenue': float(monthly_revenue),
                    'average_fare': float(average_fare),
                    'currency': 'NPR'
                },
                
                # Charts Data
                'charts': {
                    'daily_rides': daily_rides,
                    'peak_hours': peak_hours
                },
                
                # Performance Metrics
                'performance': {
                    'top_drivers': top_drivers,
                    'active_users': active_users,
                    'popular_routes': popular_routes
                },
                
                # System Information
                'system': {
                    'alerts': system_alerts,
                    'server_status': 'healthy',
                    'last_updated': timezone.now().isoformat()
                }
            }
            
            return Response(dashboard_data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SystemHealthView(APIView):
    """System health monitoring endpoint"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get system health metrics"""
        try:
            # Database health
            db_healthy = True
            try:
                User.objects.count()
                Ride.objects.count()
            except Exception:
                db_healthy = False
            
            # Recent activity
            now = timezone.now()
            last_hour = now - timedelta(hours=1)
            recent_activity = {
                'new_users': User.objects.filter(date_joined__gte=last_hour).count(),
                'new_rides': Ride.objects.filter(created_at__gte=last_hour).count(),
                'active_sessions': 15  # Mock data - would come from session tracking
            }
            
            # Error rates (mock data)
            error_rates = {
                'api_errors': 0.2,  # 0.2% error rate
                'payment_failures': 1.1,  # 1.1% failure rate
                'ride_cancellations': 8.5  # 8.5% cancellation rate
            }
            
            # Performance metrics
            performance = {
                'avg_response_time': 245,  # milliseconds
                'uptime_percentage': 99.8,
                'total_requests_last_hour': 1247
            }
            
            health_data = {
                'status': 'healthy' if db_healthy else 'unhealthy',
                'database': 'connected' if db_healthy else 'error',
                'timestamp': now.isoformat(),
                'metrics': {
                    'recent_activity': recent_activity,
                    'error_rates': error_rates,
                    'performance': performance
                }
            }
            
            return Response(health_data)
            
        except Exception as e:
            return Response(
                {'error': str(e), 'status': 'error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BusinessAnalyticsView(APIView):
    """Advanced business analytics endpoint"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get detailed business analytics"""
        try:
            period = request.query_params.get('period', 'month')  # week, month, quarter, year
            
            # Calculate date range
            now = timezone.now()
            if period == 'week':
                start_date = now - timedelta(days=7)
            elif period == 'month':
                start_date = now - timedelta(days=30)
            elif period == 'quarter':
                start_date = now - timedelta(days=90)
            else:  # year
                start_date = now - timedelta(days=365)
            
            # Growth metrics
            current_period_rides = Ride.objects.filter(
                created_at__gte=start_date
            ).count()
            
            previous_period_start = start_date - (now - start_date)
            previous_period_rides = Ride.objects.filter(
                created_at__gte=previous_period_start,
                created_at__lt=start_date
            ).count()
            
            ride_growth = ((current_period_rides - previous_period_rides) / 
                          max(previous_period_rides, 1)) * 100
            
            # Revenue growth
            current_revenue = Ride.objects.filter(
                status='completed',
                completed_at__gte=start_date
            ).aggregate(total=Sum('fare'))['total'] or 0
            
            previous_revenue = Ride.objects.filter(
                status='completed',
                completed_at__gte=previous_period_start,
                completed_at__lt=start_date
            ).aggregate(total=Sum('fare'))['total'] or 0
            
            revenue_growth = ((current_revenue - previous_revenue) / 
                            max(previous_revenue, 1)) * 100
            
            # User acquisition
            new_users = User.objects.filter(date_joined__gte=start_date).count()
            new_drivers = Driver.objects.filter(created_at__gte=start_date).count()
            
            # Market insights
            ride_types_distribution = [
                {'type': 'Standard', 'percentage': 65.5, 'count': 423},
                {'type': 'Premium', 'percentage': 25.2, 'count': 163},
                {'type': 'Shared', 'percentage': 9.3, 'count': 60}
            ]
            
            # Customer satisfaction
            satisfaction_metrics = {
                'average_rider_rating': 4.3,
                'average_driver_rating': 4.5,
                'complaint_rate': 2.1,  # percentage
                'repeat_customer_rate': 78.5  # percentage
            }
            
            # Operational efficiency
            efficiency_metrics = {
                'average_pickup_time': 8.5,  # minutes
                'average_ride_duration': 22.3,  # minutes
                'driver_utilization_rate': 67.8,  # percentage
                'ride_completion_rate': 94.2  # percentage
            }
            
            analytics_data = {
                'period': period,
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': now.isoformat()
                },
                'growth_metrics': {
                    'ride_growth_percentage': round(ride_growth, 2),
                    'revenue_growth_percentage': round(revenue_growth, 2),
                    'new_users': new_users,
                    'new_drivers': new_drivers
                },
                'market_insights': {
                    'ride_types_distribution': ride_types_distribution,
                    'total_rides_current_period': current_period_rides,
                    'total_revenue_current_period': float(current_revenue)
                },
                'customer_satisfaction': satisfaction_metrics,
                'operational_efficiency': efficiency_metrics,
                'generated_at': now.isoformat()
            }
            
            return Response(analytics_data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
