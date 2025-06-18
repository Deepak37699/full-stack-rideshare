# Ride Sharing Application - Copilot Instructions

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview

This is a full-stack ride sharing application with:

- **Backend**: Django REST API with real-time capabilities
- **Frontend**: Flutter cross-platform mobile app
- **Package Manager**: uv for Python dependencies

## Architecture & Technologies

### Backend (Django)

- Django 5.2+ with Django REST Framework
- WebSocket support via Django Channels
- JWT authentication with SimpleJWT
- Redis for caching and real-time features
- Celery for background tasks
- PostgreSQL database (production)

### Frontend (Flutter)

- Cross-platform mobile application
- Real-time features for ride tracking
- Maps integration for location services
- Payment gateway integration

## Key Features to Implement

1. **User Authentication & Profiles**

   - User registration/login
   - Driver registration with verification
   - Profile management

2. **Ride Management**

   - Ride booking system
   - Real-time ride tracking
   - Ride history and receipts

3. **Driver Features**

   - Driver dashboard
   - Ride acceptance/rejection
   - Earnings tracking

4. **Payment System**

   - Multiple payment methods
   - Fare calculation
   - Payment processing

5. **Real-time Features**
   - Live location tracking
   - Push notifications
   - Chat between rider and driver

## Development Guidelines

- Follow Django best practices and PEP 8
- Use Django REST Framework serializers and viewsets
- Implement proper error handling and validation
- Use async views where appropriate for real-time features
- Follow Flutter/Dart conventions
- Implement responsive UI design
- Use proper state management (Provider/Bloc)

## API Design

- RESTful API endpoints
- WebSocket connections for real-time updates
- Proper HTTP status codes
- Comprehensive error responses
- API versioning when needed

## Security Considerations

- JWT token-based authentication
- Rate limiting for API endpoints
- Input validation and sanitization
- CORS configuration for frontend
- Secure payment processing
