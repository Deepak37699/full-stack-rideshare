# Modern Phone Input Field - Usage Guide

## Overview
The `ModernPhoneInputField` is a sophisticated phone number input widget that provides:
- Country selection with flags and country codes
- Automatic phone number formatting based on selected country
- Validation based on country-specific phone number formats
- Modern UI design with clean styling

## Features

### 🌍 Country Selection
- **Flag Display**: Shows country flag emoji for visual identification
- **Country Code**: Displays the international dialing code (e.g., +977, +1, +91)
- **Dropdown Interface**: Tap to open a searchable country picker bottom sheet
- **Search Functionality**: Users can search for countries by name

### 📱 Smart Formatting
- **Auto-formatting**: Phone numbers are formatted according to country standards
- **Input Validation**: Only allows numeric input with appropriate length limits
- **Real-time Updates**: Formatting updates as the user types

### 🎨 Modern Design
- **Clean Interface**: Rounded corners and modern styling
- **Visual Separation**: Country code picker is visually separated from number input
- **Consistent Theme**: Matches the app's design language

## Usage

### Basic Implementation
```dart
ModernPhoneInputField(
  controller: _phoneController,
  labelText: 'Phone Number',
  hintText: 'Enter your phone number',
)
```

### Advanced Implementation
```dart
ModernPhoneInputField(
  controller: _phoneController,
  labelText: 'Phone Number / फोन नम्बर',
  hintText: '98XXXXXXXX',
  initialCountryCode: 'NP', // Default to Nepal
  onCountryChanged: (countryCode) {
    setState(() {
      _selectedCountryCode = countryCode;
    });
  },
  validator: (value) {
    // Custom validation logic
    return null;
  },
)
```

## API Reference

### Properties
- `controller` (required): TextEditingController for the phone number input
- `labelText`: Label text displayed above the field
- `hintText`: Placeholder text in the input field
- `isRequired`: Whether the field is required (default: true)
- `validator`: Custom validation function
- `onCountryChanged`: Callback when country is changed
- `initialCountryCode`: Default country code (ISO 2-letter code)

### Methods
- `getFullPhoneNumber()`: Returns complete phone number with country code
- `isValidPhoneNumber()`: Validates phone number based on selected country

## Country-Specific Formatting

### Supported Countries
- **Nepal (NP)**: +977 XXXX-XXXXXXX
- **USA/Canada (US/CA)**: +1 (XXX) XXX-XXXX  
- **India (IN)**: +91 XXXXX-XXXXX
- **UK (GB)**: +44 XX XXXX XXXX
- **And many more...**

### Phone Number Validation
Each country has specific validation rules:
- **Nepal**: 10 digits (98XXXXXXXX format)
- **USA/Canada**: 10 digits
- **India**: 10 digits
- **Default**: 7-15 digits for other countries

## Integration with API

### Getting Formatted Phone Number
```dart
// In your registration logic
final formattedPhone = phoneToApiFormat(
  _phoneController.text.trim(), 
  _selectedCountryCode
);

// This returns: "+977XXXXXXXXXX" format
```

### Error Handling
The widget provides detailed error messages:
- "Please enter your phone number" (if empty)
- "Please enter a valid 10-digit Nepal phone number (98XXXXXXXX)" (Nepal-specific)
- "Please enter a valid phone number for [Country]" (generic)

## Styling Customization

The widget uses consistent styling with the app theme:
- **Border Color**: `Colors.grey.shade300`
- **Focus Color**: `Color(0xFF00D4AA)` (app primary color)
- **Background**: `Colors.grey.shade50` for country picker
- **Text Style**: 16px, medium weight for country code

## Best Practices

1. **Always handle country changes**: Use `onCountryChanged` to update your state
2. **Use proper validation**: The built-in validator is country-aware
3. **Format for API**: Always use `phoneToApiFormat()` before sending to backend
4. **Provide clear labels**: Include both English and local language labels
5. **Test with different countries**: Ensure your backend accepts various formats

## Dependencies

Make sure you have these dependencies in your `pubspec.yaml`:
```yaml
dependencies:
  country_picker: ^2.0.26
  flutter:
    sdk: flutter
```

## Migration from Old Phone Input

If you're migrating from the old `PhoneInputField`:

### Before:
```dart
PhoneInputField(
  controller: _phoneController,
  labelText: 'Phone Number',
  hintText: '+977 98XXXXXXXX',
)
```

### After:
```dart
ModernPhoneInputField(
  controller: _phoneController,
  labelText: 'Phone Number',
  hintText: '98XXXXXXXX',
  initialCountryCode: 'NP',
  onCountryChanged: (code) => _selectedCountryCode = code,
)
```

### API Changes:
```dart
// Old way
phoneNumber: phoneToApiFormat(_phoneController.text.trim()),

// New way  
phoneNumber: phoneToApiFormat(_phoneController.text.trim(), _selectedCountryCode),
```

## Troubleshooting

### Common Issues:
1. **Country picker not showing**: Ensure `country_picker` dependency is installed
2. **Validation errors**: Check that phone number matches country format
3. **API format issues**: Use the new `phoneToApiFormat(text, countryCode)` signature

### Debug Tips:
- Use `getFullPhoneNumber()` to see the complete formatted number
- Check `isValidPhoneNumber()` for validation status
- Monitor `onCountryChanged` callback for country selection events
