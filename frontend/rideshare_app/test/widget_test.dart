// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';

import 'package:rideshare_app/main.dart';
import 'package:rideshare_app/providers/app_providers.dart';

void main() {
  testWidgets('RideShare app smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(
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

    // Wait for the initial frame to render
    await tester.pump();

    // Verify that the app starts with splash screen
    expect(find.byType(MaterialApp), findsOneWidget);
    
    // The splash screen should be present initially with inDrive Nepal text
    expect(find.text('inDrive Nepal'), findsOneWidget);
  });
}
