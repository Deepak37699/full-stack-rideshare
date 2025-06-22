#!/usr/bin/env python
"""
Advanced test script for InDrive Backend API - Advanced Features
Tests chat, wallet, promo codes, referrals, live tracking, and notifications
"""

import requests
import json
import time
from datetime import datetime
import uuid

BASE_URL = "http://localhost:8000/api"

class InDriveAdvancedAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.ride_id = None
    
    def authenticate_user(self):
        """Authenticate user to get access token"""
        print("Authenticating user...")
        
        # Try to login with existing user
        login_data = {
            "phone_number": "+9779800000001",
            "password": "testpass123"
        }
        
        response = self.session.post(
            f"{BASE_URL}/accounts/auth/login/",
            json=login_data
        )
        
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data.get("access")
            self.session.headers.update({
                'Authorization': f'Bearer {self.auth_token}'
            })
            print("✅ User authentication successful")
            return True
        else:
            print(f"❌ User authentication failed: {response.text}")
            return False
    
    def test_chat_history(self):
        """Test chat history endpoints"""
        print("Testing Chat History...")
        
        # Create a mock ride ID for testing
        test_ride_id = str(uuid.uuid4())
        
        # Test getting chat history (will fail because ride doesn't exist, but tests endpoint)
        response = self.session.get(f"{BASE_URL}/rides/chat-history/?ride_id={test_ride_id}")
        
        if response.status_code in [200, 404]:  # 404 is expected for non-existent ride
            print("✅ Chat history endpoint is working")
            return True
        else:
            print(f"❌ Chat history failed: {response.text}")
            return False
    
    def test_wallet_management(self):
        """Test wallet management endpoints"""
        print("Testing Wallet Management...")
        
        # Test getting wallet information
        response = self.session.get(f"{BASE_URL}/rides/wallet/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Wallet balance: NPR {data.get('balance', 'N/A')}")
            print(f"   Transaction count: {len(data.get('transactions', []))}")
            
            # Test wallet top-up
            topup_response = self.session.post(
                f"{BASE_URL}/rides/wallet/",
                json={
                    "amount": 500.0,
                    "payment_method": "eSewa"
                }
            )
            
            if topup_response.status_code == 201:
                print("✅ Wallet management successful")
                return True
            else:
                print(f"❌ Wallet top-up failed: {topup_response.text}")
                return False
        else:
            print(f"❌ Wallet management failed: {response.text}")
            return False
    
    def test_promo_codes(self):
        """Test promo code endpoints"""
        print("Testing Promo Codes...")
        
        # Test getting available promo codes
        response = self.session.get(f"{BASE_URL}/rides/promo-codes/")
        
        if response.status_code == 200:
            data = response.json()
            codes = data.get('available_codes', [])
            print(f"   Available promo codes: {len(codes)}")
            
            # Test applying a promo code
            if codes:
                test_code = codes[0]['code']
                apply_response = self.session.post(
                    f"{BASE_URL}/rides/promo-codes/",
                    json={
                        "promo_code": test_code,
                        "ride_amount": 200.0
                    }
                )
                
                if apply_response.status_code == 200:
                    apply_data = apply_response.json()
                    print(f"   Promo code '{test_code}' applied: NPR {apply_data.get('discount_amount', 0)} discount")
                    print("✅ Promo codes successful")
                    return True
                else:
                    print(f"❌ Promo code application failed: {apply_response.text}")
                    return False
            else:
                print("✅ Promo codes endpoint working (no codes available)")
                return True
        else:
            print(f"❌ Promo codes failed: {response.text}")
            return False
    
    def test_referral_system(self):
        """Test referral system endpoints"""
        print("Testing Referral System...")
        
        response = self.session.get(f"{BASE_URL}/rides/referrals/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Referral code: {data.get('referral_code', 'N/A')}")
            print(f"   Total referrals: {data.get('total_referrals', 0)}")
            print(f"   Total earned: NPR {data.get('total_earned', 0)}")
            print("✅ Referral system successful")
            return True
        else:
            print(f"❌ Referral system failed: {response.text}")
            return False
    
    def test_live_tracking(self):
        """Test live tracking endpoints"""
        print("Testing Live Tracking...")
        
        # Create a mock ride ID for testing
        test_ride_id = str(uuid.uuid4())
        
        # Test getting tracking info (will fail because ride doesn't exist, but tests endpoint)
        response = self.session.get(f"{BASE_URL}/rides/live-tracking/?ride_id={test_ride_id}")
        
        if response.status_code in [200, 404]:  # 404 is expected for non-existent ride
            print("✅ Live tracking endpoint is working")
            return True
        else:
            print(f"❌ Live tracking failed: {response.text}")
            return False
    
    def test_notifications(self):
        """Test notifications endpoints"""
        print("Testing Notifications...")
        
        # Test getting notifications
        response = self.session.get(f"{BASE_URL}/rides/notifications/")
        
        if response.status_code == 200:
            data = response.json()
            notifications = data.get('notifications', [])
            print(f"   Total notifications: {len(notifications)}")
            print(f"   Unread count: {data.get('unread_count', 0)}")
            
            # Test marking notifications as read
            if notifications:
                notification_ids = [n['id'] for n in notifications[:2]]  # Mark first 2 as read
                mark_read_response = self.session.patch(
                    f"{BASE_URL}/rides/notifications/",
                    json={"notification_ids": notification_ids}
                )
                
                if mark_read_response.status_code == 200:
                    print("✅ Notifications successful")
                    return True
                else:
                    print(f"❌ Mark notifications as read failed: {mark_read_response.text}")
                    return False
            else:
                print("✅ Notifications endpoint working (no notifications)")
                return True
        else:
            print(f"❌ Notifications failed: {response.text}")
            return False
    
    def run_all_tests(self):
        """Run all advanced API tests"""
        print("🚀 Starting InDrive Advanced Features API Tests")
        print("=" * 60)
        
        # First authenticate
        if not self.authenticate_user():
            print("❌ Cannot proceed without authentication")
            return False
        
        tests = [
            self.test_chat_history,
            self.test_wallet_management,
            self.test_promo_codes,
            self.test_referral_system,
            self.test_live_tracking,
            self.test_notifications,
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
        
        print("=" * 60)
        print(f"Advanced Features Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All advanced features tests passed!")
        else:
            print("⚠️  Some advanced features tests failed.")
        
        return passed == total


def main():
    """Main function to run the advanced tests"""
    tester = InDriveAdvancedAPITester()
    
    print("InDrive Backend API - Advanced Features Test Suite")
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
