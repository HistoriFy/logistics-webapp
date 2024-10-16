import json
from channels.generic.websocket import AsyncWebsocketConsumer

class BookingStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
        else:
            self.user = user
            self.group_name = f'user_{self.user.id}_bookings'

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
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['message']))
    
    async def send_otp_update(self, event):
        # Send the OTP to the user via WebSocket
        await self.send(text_data=json.dumps({
            'otp': event['otp'],
            'message': 'Your booking has been accepted. Here is your OTP to start the trip.'
        }))