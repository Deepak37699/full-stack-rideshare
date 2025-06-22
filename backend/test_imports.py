#!/usr/bin/env python
"""
Test script to verify Django imports work correctly
"""

import os
import sys
import django

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rideshare.settings')

# Setup Django
django.setup()

# Now test imports
try:
    from django.conf import settings
    from django.db import models
    from rest_framework import viewsets
    from django.utils import timezone
    from django.contrib.auth.models import User
    
    print("✅ All Django imports successful!")
    print(f"✅ Django version: {django.get_version()}")
    print("✅ Settings configured properly")
    print("✅ REST Framework available")
    print("✅ IDE configuration should now work correctly")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Configuration error: {e}")
