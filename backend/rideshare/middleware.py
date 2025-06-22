import time
import json
from django.http import JsonResponse
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    """Middleware for API rate limiting"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Rate limits per endpoint (requests per minute)
        self.rate_limits = {
            '/api/rides/fare-estimate/': 30,
            '/api/rides/nearby-drivers/': 20,
            '/api/rides/match-ride/': 5,
            '/api/rides/geocode/': 50,
            '/api/rides/emergency-alert/': 10,
            'default': 100
        }
    
    def __call__(self, request):
        if request.path.startswith('/api/'):
            if not self._check_rate_limit(request):
                return JsonResponse({
                    'error': 'Rate limit exceeded. Please try again later.',
                    'retry_after': 60
                }, status=429)
        
        response = self.get_response(request)
        return response
    
    def _check_rate_limit(self, request):
        """Check if request is within rate limits"""
        # Get user identifier
        if hasattr(request, 'user') and request.user.is_authenticated:
            identifier = f"user_{request.user.id}"
        else:
            identifier = f"ip_{self._get_client_ip(request)}"
        
        # Get rate limit for endpoint
        endpoint = request.path
        rate_limit = self.rate_limits.get(endpoint, self.rate_limits['default'])
        
        # Create cache key
        cache_key = f"rate_limit_{identifier}_{endpoint}_{int(time.time() // 60)}"
        
        # Get current count
        current_count = cache.get(cache_key, 0)
        
        if current_count >= rate_limit:
            return False
        
        # Increment count
        cache.set(cache_key, current_count + 1, 60)  # 60 seconds timeout
        return True
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RequestLoggingMiddleware:
    """Middleware for logging API requests and responses"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        # Log request
        if request.path.startswith('/api/'):
            self._log_request(request)
        
        response = self.get_response(request)
        
        # Log response
        if request.path.startswith('/api/'):
            duration = time.time() - start_time
            self._log_response(request, response, duration)
        
        return response
    
    def _log_request(self, request):
        """Log incoming API request"""
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'method': request.method,
            'path': request.path,
            'user': request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None,
            'ip': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        }
        
        # Log request body for POST/PUT/PATCH requests (excluding sensitive data)
        if request.method in ['POST', 'PUT', 'PATCH'] and hasattr(request, 'body'):
            try:
                body = json.loads(request.body.decode('utf-8'))
                # Remove sensitive fields
                sensitive_fields = ['password', 'token', 'secret']
                for field in sensitive_fields:
                    if field in body:
                        body[field] = '***'
                log_data['body'] = body
            except:
                pass
        
        logger.info(f"API Request: {json.dumps(log_data)}")
    
    def _log_response(self, request, response, duration):
        """Log API response"""
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'user': request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None,
        }
        
        logger.info(f"API Response: {json.dumps(log_data)}")
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware:
    """Middleware for adding security headers"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers for API endpoints
        if request.path.startswith('/api/'):
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            response['Content-Security-Policy'] = "default-src 'self'"
        
        return response


class APIVersionMiddleware:
    """Middleware for API versioning"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.default_version = 'v1'
    
    def __call__(self, request):
        if request.path.startswith('/api/'):
            # Extract version from header or URL
            version = request.META.get('HTTP_API_VERSION', self.default_version)
            request.api_version = version
        
        response = self.get_response(request)
        
        # Add version to response headers
        if request.path.startswith('/api/'):
            response['API-Version'] = getattr(request, 'api_version', self.default_version)
        
        return response


class CorsMiddleware:
    """Custom CORS middleware for API endpoints"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        if request.path.startswith('/api/'):
            # Add CORS headers
            response['Access-Control-Allow-Origin'] = '*'  # In production, use specific domains
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, API-Version'
            response['Access-Control-Max-Age'] = '86400'
        
        return response
