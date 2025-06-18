# Ride Sharing Application

A comprehensive full-stack ride sharing application built with Django REST API backend and Flutter cross-platform frontend.

## Project Overview

This ride sharing application provides a complete platform for connecting riders with drivers, featuring real-time location tracking, secure payments, and comprehensive ride management.

### Technologies Used

#### Backend

- **Django 5.2+** - Web framework
- **Django REST Framework** - API development
- **Django Channels** - WebSocket support for real-time features
- **JWT Authentication** - Secure user authentication
- **Redis** - Caching and real-time messaging
- **Celery** - Background task processing
- **PostgreSQL** - Production database (SQLite for development)
- **uv** - Python package manager

#### Frontend

- **Flutter** - Cross-platform mobile development
- **Provider/Bloc** - State management
- **HTTP/Dio** - API communication
- **Google Maps** - Maps and location services
- **Hive** - Local storage
- **Socket.IO** - Real-time communication

## Features

### User Management

- [x] User registration and authentication
- [x] Driver registration with document verification
- [x] Profile management
- [x] Role-based access (Rider/Driver/Admin)

### Ride Management

- [x] Ride booking system
- [x] Real-time ride tracking
- [x] Driver-rider matching algorithm
- [x] Ride history and receipts
- [x] Rating and review system

### Driver Features

- [x] Driver dashboard
- [x] Online/offline status management
- [x] Ride acceptance/rejection
- [x] Earnings tracking
- [x] Document upload and verification

### Payment System

- [x] Multiple payment methods
- [x] Secure payment processing
- [x] Automatic fare calculation
- [x] Driver payouts
- [x] Refund management

### Real-time Features

- [x] Live location tracking
- [x] Push notifications
- [x] WebSocket communication
- [x] Real-time ride updates

## Project Structure

```
├── backend/                 # Django Backend
│   ├── rideshare/          # Main Django project
│   ├── accounts/           # User management
│   ├── rides/              # Ride management
│   ├── drivers/            # Driver-specific features
│   ├── payments/           # Payment processing
│   ├── manage.py
│   ├── pyproject.toml      # uv configuration
│   └── requirements files
│
├── frontend/               # Flutter Frontend
│   └── rideshare_app/     # Flutter application
│       ├── lib/           # Dart source code
│       ├── android/       # Android-specific files
│       ├── ios/           # iOS-specific files
│       └── pubspec.yaml   # Flutter dependencies
│
└── .github/
    └── copilot-instructions.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- uv (Python package manager)
- Flutter SDK 3.8+
- Redis server
- PostgreSQL (for production)

### Backend Setup

1. **Navigate to backend directory:**

   ```bash
   cd backend
   ```

2. **Install dependencies:**

   ```bash
   uv sync
   ```

3. **Set up environment variables:**
   Create a `.env` file in the backend directory:

   ```env
   SECRET_KEY=your_secret_key_here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

4. **Run migrations:**

   ```bash
   uv run python manage.py makemigrations
   uv run python manage.py migrate
   ```

5. **Create superuser:**

   ```bash
   uv run python manage.py createsuperuser
   ```

6. **Start development server:**
   ```bash
   uv run python manage.py runserver
   ```

### Frontend Setup

1. **Navigate to frontend directory:**

   ```bash
   cd frontend/rideshare_app
   ```

2. **Install dependencies:**

   ```bash
   flutter pub get
   ```

3. **Run the app:**
   ```bash
   flutter run
   ```

## API Endpoints

### Authentication

- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Token refresh

### User Management

- `GET/POST /api/accounts/users/` - User CRUD operations
- `POST /api/accounts/register/` - User registration
- `GET /api/accounts/me/` - Current user info

### Rides

- `GET/POST /api/rides/rides/` - Ride CRUD operations
- `POST /api/rides/request-ride/` - Request a ride
- `GET /api/rides/nearby-drivers/` - Find nearby drivers
- `POST /api/rides/{id}/accept/` - Accept a ride
- `POST /api/rides/{id}/start/` - Start a ride
- `POST /api/rides/{id}/complete/` - Complete a ride

### Drivers

- `GET/POST /api/drivers/drivers/` - Driver CRUD operations
- `POST /api/drivers/register/` - Driver registration
- `GET /api/drivers/status/` - Driver status
- `GET /api/drivers/earnings/` - Driver earnings

### Payments

- `GET/POST /api/payments/payment-methods/` - Payment method management
- `POST /api/payments/process-payment/` - Process payment
- `GET /api/payments/earnings/` - Driver earnings

## Development

### Database Models

#### User Model (accounts/models.py)

- Custom user model extending AbstractUser
- Support for rider/driver roles
- Profile information and location tracking

#### Ride Model (rides/models.py)

- Complete ride lifecycle management
- Real-time location tracking
- Rating and review system

#### Driver Model (drivers/models.py)

- Driver profile and vehicle information
- Document verification system
- Earnings and rating tracking

#### Payment Model (payments/models.py)

- Payment processing and methods
- Driver earnings and payouts
- Refund management

### Real-time Features

The application uses Django Channels with Redis for real-time features:

- Live ride tracking
- Driver location updates
- Instant notifications
- Chat between rider and driver

### Security

- JWT-based authentication
- Rate limiting on API endpoints
- Input validation and sanitization
- CORS configuration
- Secure payment processing

## Testing

### Backend Tests

```bash
cd backend
uv run python manage.py test
```

### Frontend Tests

```bash
cd frontend/rideshare_app
flutter test
```

## Deployment

### Backend Deployment

1. Set up PostgreSQL database
2. Configure environment variables
3. Collect static files: `uv run python manage.py collectstatic`
4. Run migrations: `uv run python manage.py migrate`
5. Deploy using your preferred method (Docker, Heroku, AWS, etc.)

### Frontend Deployment

1. Build for production: `flutter build apk` or `flutter build ios`
2. Deploy to app stores or distribute APK/IPA files

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and commit: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/new-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the GitHub repository.

---

**Note:** This is a complete ride sharing application template. Make sure to customize the configuration, add proper API keys for maps and payment services, and implement additional security measures before deploying to production.
