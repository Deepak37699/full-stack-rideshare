# InDrive Clone - Full Stack Ride Sharing App

A complete InDrive-style ride sharing application built with Django backend and Flutter frontend.

## 🚀 Features

### 🔐 Authentication & User Management
- User registration and login with OTP verification
- Driver registration with document verification
- Profile management with photo upload
- Multi-language support (English, Nepali)

### 🚗 Ride Management
- Real-time ride booking and matching
- Live GPS tracking during rides
- Ride history and receipts
- Multiple vehicle types support
- Dynamic pricing based on distance and demand

### 💰 Payment System
- Multiple payment methods (Cash, Digital Wallets)
- Secure payment processing
- Automatic fare calculation
- Promo codes and discounts
- Driver earnings management

### 📱 Real-time Features
- WebSocket-based live tracking
- Push notifications
- In-app messaging between riders and drivers
- SOS emergency features

### 📊 Analytics & Admin
- Comprehensive admin dashboard
- Driver performance analytics
- Revenue tracking and reporting
- User behavior insights

## 🛠 Tech Stack

### Backend
- **Django 5.2+** with Django REST Framework
- **WebSocket** support via Django Channels
- **JWT Authentication** with SimpleJWT
- **Redis** for caching and real-time features
- **Celery** for background tasks
- **PostgreSQL** database

### Frontend
- **Flutter** cross-platform mobile app
- **Real-time** location services
- **Maps** integration
- **Payment** gateway integration

## 📋 Prerequisites

- Python 3.11+
- Flutter 3.0+
- Redis server
- PostgreSQL (for production)

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Deepak37699/full-stack-rideshare.git
   cd full-stack-rideshare
   ```

2. **Backend Setup**
   ```bash
   cd backend
   uv sync
   uv run python manage.py migrate
   uv run python manage.py runserver
   ```

3. **Frontend Setup**
   ```bash
   cd frontend/rideshare_app
   flutter pub get
   flutter run
   ```

## 📚 Documentation

- [Backend API Documentation](backend/README.md)
- [Frontend Documentation](frontend/rideshare_app/README.md)
- [Quick Start Guide](QUICKSTART.md)

## 🧪 Testing

### Backend Tests
```bash
cd backend
uv run python -m pytest test_complete_api.py -v
```

### Frontend Tests
```bash
cd frontend/rideshare_app
flutter test
```

## 🔧 Development Tasks

Available VS Code tasks:
- `Django: Run Development Server`
- `Flutter: Run App`
- `Setup: Install All Dependencies`
- `Django: Make Migrations`
- `Django: Migrate Database`

## 📦 Deployment

### Backend Deployment
1. Set environment variables
2. Configure PostgreSQL database
3. Set up Redis server
4. Deploy to your preferred platform (Heroku, DigitalOcean, AWS)

### Frontend Deployment
1. Build for Android: `flutter build apk`
2. Build for iOS: `flutter build ios`
3. Deploy to app stores

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Deepak Yadav** ([@Deepak37699](https://github.com/Deepak37699))

## 🙏 Acknowledgments

- Inspired by InDrive's innovative ride-sharing model
- Built with modern technologies for scalability and performance

---

**Note**: This is a complete, production-ready ride sharing application with all major features implemented. The email configuration has been updated to ensure proper GitHub contribution tracking.
