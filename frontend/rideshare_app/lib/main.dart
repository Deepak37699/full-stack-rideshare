import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/app_providers.dart';
import 'screens/splash_screen.dart';
import 'screens/onboarding_screen.dart';
import 'screens/auth_choice_screen.dart';
import 'screens/login_screen.dart';
import 'screens/register_screen.dart';
import 'screens/home_screen.dart';
import 'screens/ride_search_screen.dart';
import 'screens/driver_offers_screen.dart';
import 'screens/ride_tracking_screen.dart';
import 'screens/driver_registration_screen.dart';
import 'screens/chat_screen.dart';
import 'screens/driver_dashboard_screen.dart';
import 'screens/ride_history_detailed_screen.dart';
import 'screens/map_screen.dart';
import 'screens/enhanced_map_screen.dart';
import 'screens/earnings_screen.dart';
import 'screens/settings_screen.dart';
import 'screens/notifications_screen.dart';
import 'screens/help_support_screen.dart';
import 'screens/payment_methods_screen.dart';
import 'screens/safety_center_screen.dart';
import 'screens/promo_codes_screen.dart';
import 'screens/referral_screen.dart';
import 'screens/ride_booking_screen.dart';
import 'screens/wallet_screen.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => UserProvider()),
        ChangeNotifierProvider(create: (_) => RideProvider()),
        ChangeNotifierProvider(create: (_) => DriverProvider()),
        ChangeNotifierProvider(create: (_) => LocationProvider()),
        ChangeNotifierProvider(create: (_) => AppProvider()),
        ChangeNotifierProvider(create: (_) => ChatProvider()),
      ],
      child: const RideShareApp(),
    ),
  );
}

class RideShareApp extends StatelessWidget {
  const RideShareApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'inDrive Nepal',
      theme: ThemeData(
        primarySwatch: Colors.teal,
        primaryColor: const Color(0xFF00D4AA),
        scaffoldBackgroundColor: Colors.white,
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF00D4AA),
          foregroundColor: Colors.white,
          elevation: 0,
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF00D4AA),
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide: const BorderSide(color: Color(0xFF00D4AA)),
          ),
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 12,
          ),
        ),
      ),
      home: const SplashScreen(),
      routes: {
        '/onboarding': (context) => const OnboardingScreen(),
        '/auth-choice': (context) => const AuthChoiceScreen(),
        '/login': (context) => const LoginScreen(),
        '/register': (context) => const RegisterScreen(),
        '/home': (context) => const HomeScreen(),
        '/ride-search': (context) => const RideSearchScreen(
          from: 'Current Location',
          to: 'Destination',
          price: '150',
        ),
        '/driver-offers': (context) => const DriverOffersScreen(),
        '/ride-tracking': (context) => const RideTrackingScreen(),
        '/driver-registration': (context) => const DriverRegistrationScreen(),
        '/chat': (context) => const ChatScreen(),
        '/driver-dashboard': (context) => const DriverDashboardScreen(),
        '/ride-history': (context) => const RideHistoryScreen(),
        '/map': (context) => const MapScreen(),
        '/enhanced-map': (context) => const EnhancedMapScreen(),
        '/earnings': (context) => const EarningsScreen(),
        '/settings': (context) => const SettingsScreen(),
        '/notifications': (context) => const NotificationsScreen(),
        '/help-support': (context) => const HelpSupportScreen(),
        '/payment-methods': (context) => const PaymentMethodsScreen(),
        '/safety-center': (context) => const SafetyCenterScreen(),
        '/promo-codes': (context) => const PromoCodesScreen(),
        '/referral': (context) => const ReferralScreen(),
        '/ride-booking': (context) => const RideBookingScreen(),
        '/wallet': (context) => const WalletScreen(),
      },
      debugShowCheckedModeBanner: false,
    );
  }
}
