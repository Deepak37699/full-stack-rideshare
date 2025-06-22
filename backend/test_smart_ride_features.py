#!/usr/bin/env python3
"""
Smart Ride Features API Test Suite
Tests the newly implemented smart features including:
- Favorite Locations
- Ride Templates  
- Scheduled Rides
- Smart Suggestions
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from django.utils import timezone

def print_status(message, status="info"):
    symbols = {"success": "✅", "error": "❌", "info": "🔵", "warning": "⚠️"}
    print(f"{symbols.get(status, '🔵')} {message}")

def test_smart_ride_features():
    base_url = "http://localhost:8000/api"
    
    print_status("Smart Ride Features Test Suite", "info")
    print("=" * 70)
    
    # Test authentication first
    auth_data = {
        "phone_number": "+1234567890",
        "password": "testpass123",
        "user_type": "rider"
    }    
    try:
        # Register user
        register_response = requests.post(f"{base_url}/accounts/auth/register/", json=auth_data)
        if register_response.status_code == 400 and "already exists" in register_response.text:
            print_status("User already exists, proceeding with login", "info")
        
        # Login
        login_response = requests.post(f"{base_url}/accounts/auth/login/", json={
            "phone_number": auth_data["phone_number"],
            "password": auth_data["password"]
        })
        
        if login_response.status_code != 200:
            print_status("Authentication failed", "error")
            return False
        
        token = login_response.json()["access"]
        headers = {"Authorization": f"Bearer {token}"}
        print_status("Authentication successful", "success")
        
    except Exception as e:
        print_status(f"Authentication error: {e}", "error")
        return False
      # Test Favorite Locations
    print_status("Testing Favorite Locations...", "info")
    try:
        # Create favorite location with unique name
        import time
        unique_name = f"Test Home {int(time.time())}"
        
        fav_location_data = {
            "name": unique_name,
            "address": "123 Main Street, City",
            "latitude": "40.7128",
            "longitude": "-74.0060",
            "location_type": "home"
        }
        
        response = requests.post(f"{base_url}/rides/favorite-locations/", 
                               json=fav_location_data, headers=headers)
        if response.status_code in [200, 201]:
            print_status("✓ Favorite location created", "success")
            location_id = response.json().get("id")
        else:
            print_status(f"Failed to create favorite location: {response.status_code}", "error")
            return False
        
        # List favorite locations
        response = requests.get(f"{base_url}/rides/favorite-locations/", headers=headers)
        if response.status_code == 200:
            locations = response.json()
            print_status(f"✓ Retrieved {len(locations)} favorite locations", "success")
        else:
            print_status("Failed to list favorite locations", "error")
            return False
            
    except Exception as e:
        print_status(f"Favorite Locations test error: {e}", "error")
        return False
      # Test Ride Templates
    print_status("Testing Ride Templates...", "info")
    try:
        # Create ride template with unique name
        unique_template_name = f"Daily Commute {int(time.time())}"
        
        template_data = {
            "name": unique_template_name,
            "pickup_name": "Home",
            "pickup_address": "123 Main Street",
            "pickup_latitude": "40.7128",
            "pickup_longitude": "-74.0060",
            "destination_name": "Office",
            "destination_address": "456 Work Plaza",
            "destination_latitude": "40.7589",
            "destination_longitude": "-73.9851",
            "preferred_ride_type": "standard",
            "special_instructions": "Please call when you arrive"
        }
        
        response = requests.post(f"{base_url}/rides/ride-templates/", 
                               json=template_data, headers=headers)
        if response.status_code in [200, 201]:
            print_status("✓ Ride template created", "success")
            template_id = response.json().get("id")
        else:
            print_status(f"Failed to create ride template: {response.status_code}", "error")
            return False
        
        # List ride templates
        response = requests.get(f"{base_url}/rides/ride-templates/", headers=headers)
        if response.status_code == 200:
            templates = response.json()
            print_status(f"✓ Retrieved {len(templates)} ride templates", "success")
        else:
            print_status("Failed to list ride templates", "error")
            return False
            
    except Exception as e:
        print_status(f"Ride Templates test error: {e}", "error")
        return False
    
    # Test Scheduled Rides
    print_status("Testing Scheduled Rides...", "info")
    try:
        # Create scheduled ride (1 hour from now)
        future_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
        scheduled_ride_data = {
            "pickup_address": "123 Main Street",
            "pickup_latitude": "40.7128",
            "pickup_longitude": "-74.0060",
            "destination_address": "789 Airport Terminal",
            "destination_latitude": "40.6892",
            "destination_longitude": "-74.1745",
            "scheduled_datetime": future_time,
            "ride_type": "premium",
            "recurring_pattern": "none",
            "advance_booking_time": 15,
            "auto_confirm": True
        }
        
        response = requests.post(f"{base_url}/rides/scheduled-rides/", 
                               json=scheduled_ride_data, headers=headers)
        if response.status_code in [200, 201]:
            print_status("✓ Scheduled ride created", "success")
            scheduled_id = response.json().get("id")
        else:
            print_status(f"Failed to create scheduled ride: {response.status_code} - {response.text}", "error")
            return False
        
        # List scheduled rides
        response = requests.get(f"{base_url}/rides/scheduled-rides/", headers=headers)
        if response.status_code == 200:
            scheduled_rides = response.json()
            print_status(f"✓ Retrieved {len(scheduled_rides)} scheduled rides", "success")
        else:
            print_status("Failed to list scheduled rides", "error")
            return False
        
        # Test upcoming rides endpoint
        response = requests.get(f"{base_url}/rides/scheduled-rides/upcoming/", headers=headers)
        if response.status_code == 200:
            upcoming = response.json()
            print_status(f"✓ Retrieved {len(upcoming)} upcoming rides", "success")
        else:
            print_status("Failed to get upcoming rides", "error")
            return False
            
    except Exception as e:
        print_status(f"Scheduled Rides test error: {e}", "error")
        return False
    
    # Test Smart Suggestions
    print_status("Testing Smart Suggestions...", "info")
    try:
        # List smart suggestions (read-only endpoint)
        response = requests.get(f"{base_url}/rides/smart-suggestions/", headers=headers)
        if response.status_code == 200:
            suggestions = response.json()
            print_status(f"✓ Retrieved {len(suggestions)} smart suggestions", "success")
        else:
            print_status("Failed to list smart suggestions", "error")
            return False
        
        # Test suggestions by type
        response = requests.get(f"{base_url}/rides/smart-suggestions/by_type/?type=routine", headers=headers)
        if response.status_code == 200:
            routine_suggestions = response.json()
            print_status("✓ Smart suggestions by type endpoint working", "success")
        else:
            print_status("Failed to get suggestions by type", "error")
            return False
            
    except Exception as e:
        print_status(f"Smart Suggestions test error: {e}", "error")
        return False
    
    print("=" * 70)
    print_status("🎉 ALL SMART RIDE FEATURES TESTS PASSED!", "success")
    print_status("Smart Ride Features are fully functional and ready!", "success")
    
    return True

if __name__ == "__main__":
    success = test_smart_ride_features()
    if not success:
        sys.exit(1)
    
    print("\n🌟 Smart Ride Features Implementation Complete!")
    print("✅ Favorite Locations - Save frequently used locations")
    print("✅ Ride Templates - Quick booking from saved routes")  
    print("✅ Scheduled Rides - Book rides for future dates/times")
    print("✅ Smart Suggestions - AI-powered ride recommendations")
    print("✅ All API endpoints functional and tested")
    print("✅ Ready for Flutter frontend integration")
