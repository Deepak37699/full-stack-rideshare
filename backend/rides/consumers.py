import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Ride, RideLocation
from drivers.models import Driver
from django.utils import timezone
from decimal import Decimal

User = get_user_model()

class RideConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time ride tracking"""
    
    async def connect(self):
        self.ride_id = self.scope['url_route']['kwargs']['ride_id']
        self.ride_group_name = f'ride_{self.ride_id}'
        
        # Join ride group
        await self.channel_layer.group_add(
            self.ride_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave ride group
        await self.channel_layer.group_discard(
            self.ride_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', '')
        
        if message_type == 'location_update':
            await self.handle_location_update(text_data_json)
        elif message_type == 'status_update':
            await self.handle_status_update(text_data_json)
        elif message_type == 'message':
            await self.handle_chat_message(text_data_json)
    
    async def handle_location_update(self, data):
        """Handle driver location updates"""
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        speed = data.get('speed', 0)
        
        if latitude and longitude:
            # Save location to database
            await self.save_ride_location(latitude, longitude, speed)
            
            # Broadcast to ride group
            await self.channel_layer.group_send(
                self.ride_group_name,
                {
                    'type': 'location_update',
                    'latitude': latitude,
                    'longitude': longitude,
                    'speed': speed,
                    'timestamp': timezone.now().isoformat()
                }
            )
    
    async def handle_status_update(self, data):
        """Handle ride status updates"""
        status = data.get('status')
        
        if status:
            await self.update_ride_status(status)
            
            # Broadcast to ride group
            await self.channel_layer.group_send(
                self.ride_group_name,
                {
                    'type': 'status_update',
                    'status': status,
                    'timestamp': timezone.now().isoformat()
                }
            )
    
    async def handle_chat_message(self, data):
        """Handle chat messages between rider and driver"""
        message = data.get('message', '')
        sender_id = data.get('sender_id')
        
        if message and sender_id:
            # Broadcast to ride group
            await self.channel_layer.group_send(
                self.ride_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_id': sender_id,
                    'timestamp': timezone.now().isoformat()
                }
            )
    
    # Send methods for different message types
    async def location_update(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def status_update(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
    
    # Database operations
    @database_sync_to_async
    def save_ride_location(self, latitude, longitude, speed):
        try:
            ride = Ride.objects.get(id=self.ride_id)
            RideLocation.objects.create(
                ride=ride,
                latitude=Decimal(str(latitude)),
                longitude=Decimal(str(longitude)),
                speed=Decimal(str(speed)) if speed else None
            )
        except Ride.DoesNotExist:
            pass
    
    @database_sync_to_async
    def update_ride_status(self, status):
        try:
            ride = Ride.objects.get(id=self.ride_id)
            ride.status = status
            if status == 'in_progress' and not ride.started_at:
                ride.started_at = timezone.now()
            elif status == 'completed' and not ride.completed_at:
                ride.completed_at = timezone.now()
            ride.save()
        except Ride.DoesNotExist:
            pass


class DriverConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for driver location updates and ride requests"""
    
    async def connect(self):
        self.driver_id = self.scope['url_route']['kwargs']['driver_id']
        self.driver_group_name = f'driver_{self.driver_id}'
        
        # Join driver group
        await self.channel_layer.group_add(
            self.driver_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave driver group
        await self.channel_layer.group_discard(
            self.driver_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', '')
        
        if message_type == 'location_update':
            await self.handle_driver_location_update(text_data_json)
        elif message_type == 'availability_update':
            await self.handle_availability_update(text_data_json)
    
    async def handle_driver_location_update(self, data):
        """Handle driver location updates"""
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if latitude and longitude:
            await self.update_driver_location(latitude, longitude)
    
    async def handle_availability_update(self, data):
        """Handle driver availability status updates"""
        is_available = data.get('is_available', False)
        await self.update_driver_availability(is_available)
    
    # Send methods
    async def ride_request(self, event):
        """Send ride request to driver"""
        await self.send(text_data=json.dumps(event))
    
    async def ride_cancelled(self, event):
        """Notify driver that ride was cancelled"""
        await self.send(text_data=json.dumps(event))
    
    # Database operations
    @database_sync_to_async
    def update_driver_location(self, latitude, longitude):
        try:
            driver = Driver.objects.get(id=self.driver_id)
            driver.current_latitude = Decimal(str(latitude))
            driver.current_longitude = Decimal(str(longitude))
            driver.last_location_update = timezone.now()
            driver.save()
        except Driver.DoesNotExist:
            pass
    
    @database_sync_to_async
    def update_driver_availability(self, is_available):
        try:
            driver = Driver.objects.get(id=self.driver_id)
            driver.is_available = is_available
            driver.save()
        except Driver.DoesNotExist:
            pass


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for general notifications"""
    
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.user_group_name = f'user_{self.user_id}'
        
        # Join user group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave user group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        # Handle incoming messages if needed
        pass
    
    # Send methods
    async def notification(self, event):
        """Send notification to user"""
        await self.send(text_data=json.dumps(event))
