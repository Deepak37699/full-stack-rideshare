#!/usr/bin/env python
"""
Comprehensive test script for InDrive Backend API
This script tests all the major backend functionalities
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

class InDriveAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        
    def test_user_registration(self):
        """Test user registration"""
        print("Testing User Registration...")
        
        # Use a unique phone number for each test run
        import random
        phone_suffix = random.randint(10000, 99999)
        phone_number = f"+977980{phone_suffix}"
        
        registration_data = {
            "phone_number": phone_number,
            "username": f"test_user_{int(time.time())}",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "user_type": "rider"
        }
        
        response = self.session.post(
            f"{BASE_URL}/accounts/auth/register/",
            json=registration_data
        )
        
        if response.status_code == 201:
            print("✅ User registration successful")
            self.user_data = response.json()
            self.user_data['phone_number'] = phone_number  # Store phone number for login
            return True
        else:
            print(f"❌ User registration failed: {response.text}")
            # If user exists, try to use a known user for testing
            self.user_data = {"phone_number": "+9779800000001"}
            return False
    
    def test_user_login(self):
        """Test user login"""
        print("Testing User Login...")
        
        login_data = {
            "phone_number": self.user_data.get("phone_number", "+9779800000001"),
            "password": "testpass123"
        }
        
        response = self.session.post(
            f"{BASE_URL}/accounts/auth/login/",
            json=login_data
        )
        
        if response.status_code == 200:
            print("✅ User login successful")
            data = response.json()
            self.auth_token = data.get("access")
            self.session.headers.update({
                'Authorization': f'Bearer {self.auth_token}'
            })
            return True
        else:
            print(f"❌ User login failed: {response.text}")
            return False
    
    def test_fare_estimation(self):
        """Test fare estimation API"""
        print("Testing Fare Estimation...")
        
        fare_data = {
            "pickup_latitude": 27.7172,
            "pickup_longitude": 85.3240,
            "destination_latitude": 27.7000,
            "destination_longitude": 85.3000,
            "ride_type": "standard"
        }
        
        response = self.session.post(
            f"{BASE_URL}/rides/fare-estimate/",
            json=fare_data
        )
        
        if response.status_code == 200:
            print("✅ Fare estimation successful")
            data = response.json()
            print(f"   Estimated fare: NPR {data.get('total_fare', 'N/A')}")
            print(f"   Distance: {data.get('distance_km', 'N/A')} km")
            print(f"   Duration: {data.get('estimated_minutes', 'N/A')} minutes")
            return True
        else:
            print(f"❌ Fare estimation failed: {response.text}")
            return False
    
    def test_nearby_drivers(self):
        """Test nearby drivers API"""
        print("Testing Nearby Drivers...")
        
        location_data = {
            "latitude": 27.7172,
            "longitude": 85.3240,
            "radius_km": 5
        }
        
        response = self.session.post(
            f"{BASE_URL}/rides/nearby-drivers/",
            json=location_data
        )
        
        if response.status_code == 200:
            print("✅ Nearby drivers search successful")
            data = response.json()
            print(f"   Found {data.get('total_found', 0)} drivers")
            return True
        else:
            print(f"❌ Nearby drivers search failed: {response.text}")
            return False
    
    def test_ride_request_creation(self):
        """Test ride request creation"""
        print("Testing Ride Request Creation...")
        
        ride_data = {
            "pickup_latitude": 27.7172,
            "pickup_longitude": 85.3240,
            "pickup_address": "Thamel, Kathmandu",
            "destination_latitude": 27.7000,
            "destination_longitude": 85.3000,
            "destination_address": "Patan Durbar Square",
            "ride_type": "standard",
            "special_instructions": "Please call when you arrive"
        }
        
        response = self.session.post(
            f"{BASE_URL}/rides/requests/",
            json=ride_data
        )
        
        if response.status_code == 201:
            print("✅ Ride request creation successful")
            data = response.json()
            print(f"   Ride request ID: {data.get('id', 'N/A')}")
            self.ride_request_id = data.get('id')
            return True
        else:
            print(f"❌ Ride request creation failed: {response.text}")
            return False
    
    def test_geocoding(self):
        """Test geocoding services"""
        print("Testing Geocoding Services...")
        
        # Test reverse geocoding
        geocode_data = {
            "operation": "reverse_geocode",
            "latitude": 27.7172,
            "longitude": 85.3240
        }
        
        response = self.session.post(
            f"{BASE_URL}/rides/geocode/",
            json=geocode_data
        )
        
        if response.status_code == 200:
            print("✅ Reverse geocoding successful")
            data = response.json()
            print(f"   Address: {data.get('formatted_address', 'N/A')}")
            return True
        else:
            print(f"❌ Reverse geocoding failed: {response.text}")
            return False
    
    def test_ride_analytics(self):
        """Test ride analytics"""
        print("Testing Ride Analytics...")
        
        response = self.session.get(f"{BASE_URL}/rides/analytics/?period=week")
        
        if response.status_code == 200:
            print("✅ Ride analytics successful")
            data = response.json()
            print(f"   Total rides: {data.get('total_rides', 0)}")
            print(f"   Total spent: NPR {data.get('total_spent', 0)}")
            return True
        else:
            print(f"❌ Ride analytics failed: {response.text}")
            return False
    
    def test_profile_endpoints(self):
        """Test user profile endpoints"""
        print("Testing Profile Endpoints...")
        
        response = self.session.get(f"{BASE_URL}/accounts/profile/")
        
        if response.status_code == 200:
            print("✅ Profile fetch successful")
            data = response.json()
            print(f"   User: {data.get('username', 'N/A')}")
            print(f"   Type: {data.get('user_type', 'N/A')}")
            return True
        else:
            print(f"❌ Profile fetch failed: {response.text}")
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting InDrive Backend API Tests")
        print("=" * 50)
        
        tests = [
            self.test_user_registration,
            self.test_user_login,
            self.test_profile_endpoints,
            self.test_fare_estimation,
            self.test_nearby_drivers,
            self.test_ride_request_creation,
            self.test_geocoding,
            self.test_ride_analytics,
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                print()  # Add spacing between tests
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {str(e)}")
                print()
        
        print("=" * 50)
        print(f"Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Backend is working correctly!")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        
        return passed == total


def main():
    """Main function to run the tests"""
    tester = InDriveAPITester()
    
    print("InDrive Backend API Comprehensive Test Suite")
    print(f"Testing against: {BASE_URL}")
    print(f"Test started at: {datetime.now()}")
    print()
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/accounts/")
        print("✅ Server is running and accessible")
        print()
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running or not accessible")
        print("Please start the Django development server with:")
        print("cd backend && uv run python manage.py runserver")
        return
    
    # Run all tests
    tester.run_all_tests()


if __name__ == "__main__":
    main()
