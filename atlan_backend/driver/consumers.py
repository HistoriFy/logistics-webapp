import json
from channels.generic.websocket import AsyncWebsocketConsumer

class DriverBookingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        driver = self.scope['user']
        if driver.is_anonymous:
            await self.close()
        else:
            self.driver = driver
            self.group_name = f'driver_{self.driver.id}_bookings'

            # Join group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def booking_status_update(self, event):
        # Send booking update message to WebSocket
        await self.send(text_data=json.dumps(event['message']))
        
class DriverAvailableBookingsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        driver = self.scope['user']
        if driver.is_anonymous:
            await self.close()
        else:
            self.driver = driver
            self.group_name = f'driver_{self.driver.id}_available_bookings'

            # Join group for driver available bookings
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            await self.accept()

    async def disconnect(self, close_code):
        # Leave group when driver disconnects
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def available_booking_update(self, event):
        # Send message to WebSocket with booking updates
        await self.send(text_data=json.dumps(event['message']))