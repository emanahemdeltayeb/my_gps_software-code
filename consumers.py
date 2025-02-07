# # In your api app, create a consumers.py file to handle WebSocket connections:
# FOR SPECIFIC DEVICE:
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.utils import timezone
from .models import Device

# FOR ALL ONLINE DEVICES:
class DeviceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.device_id = self.scope['url_route']['kwargs']['device_id']
        self.device_group_name = f'device_{self.device_id}'  # Group for this device
        self.global_group_name = 'all_online_devices'  # Group for all online devices

        # Add the device to its specific group
        await self.channel_layer.group_add(
            self.device_group_name,
            self.channel_name
        )

        # Add the device to the global group for all online devices
        await self.channel_layer.group_add(
            self.global_group_name,
            self.channel_name
        )

        # Update the device's online status and WebSocket channel name
        await self.update_device_status(True)
        await self.update_websocket_channel_name(self.channel_name)

        await self.accept()
        print(f"Device {self.device_id} connected.")

    async def disconnect(self, close_code):
        # Remove the device from its specific group
        await self.channel_layer.group_discard(
            self.device_group_name,
            self.channel_name
        )

        # Remove the device from the global group for all online devices
        await self.channel_layer.group_discard(
            self.global_group_name,
            self.channel_name
        )

        # Clear the device's WebSocket channel name and update its online status
        await self.clear_websocket_channel_name()
        await self.update_device_status(False)

        print(f"Device {self.device_id} disconnected.")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            coords = text_data_json['coords']

            # Update the device's current_coords and save to the database
            device = await self.update_device_coords(coords)

            # Serialize the device data
            serialized_device = await self.serialize_device(device)

            # Broadcast the serialized data to the device's specific group
            await self.channel_layer.group_send(
                self.device_group_name,
                {
                    'type': 'device_coords',
                    'device': serialized_device,  # Send serialized device data
                }
            )

            # Broadcast the serialized data to all online devices
            await self.channel_layer.group_send(
                self.global_group_name,
                {
                    'type': 'device_coords',
                    'device': serialized_device,  # Send serialized device data
                }
            )
        except Exception as e:
            print(f"Error in receive: {e}")
            await self.send(text_data=json.dumps({
                'status': 'error',
                'message': str(e)
            }))

    async def device_coords(self, event):
        # Send the serialized device data back to the WebSocket
        device_data = event['device']
        await self.send(text_data=json.dumps({
            'device': device_data,
        }))

    @sync_to_async
    def update_device_coords(self, coords):
        try:
            # Fetch the device
            device = Device.objects.get(id=self.device_id)

            # Update the current_coords field
            device.current_coords = coords

            # Append the new coordinates to the car_history
            car_history = device.car_history or []
            car_history.append({
                'timestamp': timezone.now().isoformat(),
                'coords': coords,
            })

            # Limit the car_history to the last 10 entries
            if len(car_history) > 10:
                car_history = car_history[-10:]

            # Save the updated history and current_coords
            device.car_history = car_history
            device.save()

            return device
        except Device.DoesNotExist:
            raise Exception(f"Device with ID {self.device_id} does not exist.")
        except Exception as e:
            raise Exception(f"Error updating device coordinates: {e}")

    @sync_to_async
    def serialize_device(self, device):
        from .serializers import DeviceSerializer
        try:
            # Serialize the device instance
            serializer = DeviceSerializer(device)
            return serializer.data
        except Exception as e:
            raise Exception(f"Error serializing device: {e}")

    @sync_to_async
    def update_websocket_channel_name(self, channel_name):
        try:
            # Fetch the device
            device = Device.objects.get(id=self.device_id)

            # Update the websocket_channel_name field
            device.websocket_channel_name = channel_name
            device.save()
        except Device.DoesNotExist:
            raise Exception(f"Device with ID {self.device_id} does not exist.")
        except Exception as e:
            raise Exception(f"Error updating websocket_channel_name: {e}")

    @sync_to_async
    def clear_websocket_channel_name(self):
        try:
            # Fetch the device
            device = Device.objects.get(id=self.device_id)

            # Clear the websocket_channel_name field
            device.websocket_channel_name = None
            device.save()
        except Device.DoesNotExist:
            raise Exception(f"Device with ID {self.device_id} does not exist.")
        except Exception as e:
            raise Exception(f"Error clearing websocket_channel_name: {e}")

    @sync_to_async
    def update_device_status(self, is_online):
        try:
            # Fetch the device
            device = Device.objects.get(id=self.device_id)

            # Update the is_online field
            device.is_online = is_online
            device.save()
        except Device.DoesNotExist:
            raise Exception(f"Device with ID {self.device_id} does not exist.")
        except Exception as e:
            raise Exception(f"Error updating device status: {e}")


# TCP Connection not tested yet need to know how to test it if it's work or not :

# import socket
# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from django.utils import timezone
# from asgiref.sync import sync_to_async
# from .models import Device

# class DeviceConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.device_id = self.scope['url_route']['kwargs']['device_id']
#         self.device_group_name = f'device_{self.device_id}'

#         # Add the device to a group
#         await self.channel_layer.group_add(
#             self.device_group_name,
#             self.channel_name
#         )

#         # Update the device's websocket_channel_name
#         await self.update_websocket_channel_name(self.channel_name)

#         # Initialize TCP connection to the GPS device
#         self.gps_client = await self.initialize_gps_client()

#         await self.accept()
#         print(f"Device {self.device_id} connected.")

#     async def disconnect(self, close_code):
#         # Remove the device from the group
#         await self.channel_layer.group_discard(
#             self.device_group_name,
#             self.channel_name
#         )

#         # Clear the websocket_channel_name when the device disconnects
#         await self.clear_websocket_channel_name()

#         # Close the TCP connection
#         if hasattr(self, 'gps_client') and self.gps_client:
#             self.gps_client.close()

#         print(f"Device {self.device_id} disconnected.")

#     async def receive(self, text_data):
#         try:
#             text_data_json = json.loads(text_data)
#             command = text_data_json.get('command')

#             if command:
#                 # Send the command to the GPS device via TCP
#                 response = await self.send_gps_command(command)

#                 # Broadcast the response to the group
#                 await self.channel_layer.group_send(
#                     self.device_group_name,
#                     {
#                         'type': 'device_message',
#                         'message': {
#                             'command': command,
#                             'response': response,
#                         },
#                     }
#                 )
#             else:
#                 # Handle coordinate updates (existing logic)
#                 coords = text_data_json.get('coords')
#                 if coords:
#                     device = await self.update_device_coords(coords)
#                     serialized_device = await self.serialize_device(device)
#                     await self.channel_layer.group_send(
#                         self.device_group_name,
#                         {
#                             'type': 'device_coords',
#                             'device': serialized_device,
#                         }
#                     )
#         except Exception as e:
#             print(f"Error in receive: {e}")
#             await self.send(text_data=json.dumps({
#                 'status': 'error',
#                 'message': str(e)
#             }))

#     async def device_message(self, event):
#         # Send the command response back to the WebSocket
#         message = event['message']
#         await self.send(text_data=json.dumps({
#             'message': message,
#         }))

#     async def device_coords(self, event):
#         # Send the serialized device data back to the WebSocket
#         device_data = event['device']
#         await self.send(text_data=json.dumps({
#             'device': device_data,
#         }))

#     @sync_to_async
#     def initialize_gps_client(self):
#         """Initialize a TCP connection to the GPS device."""
#         try:
#             # Replace with your GPS device's IP and port
#             host = '112.112.112.112'
#             port = 9000

#             # Create a TCP socket
#             sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             sock.connect((host, port))
#             print(f"Connected to GPS device at {host}:{port}")
#             return sock
#         except Exception as e:
#             print(f"Failed to connect to GPS device: {e}")
#             return None

#     @sync_to_async
#     def send_gps_command(self, command):
#         """Send a command to the GPS device and return the response."""
#         try:
#             if not hasattr(self, 'gps_client') or not self.gps_client:
#                 return "Error: Not connected to GPS device."

#             # Send the command
#             self.gps_client.send(command.encode())
#             print(f"Sent command: {command}")

#             # Receive the response
#             response = self.gps_client.recv(1024).decode()
#             print(f"Received response: {response}")
#             return response
#         except Exception as e:
#             return f"Error sending/receiving data: {e}"

#     @sync_to_async
#     def update_device_coords(self, coords):
#         """Update the device's coordinates in the database."""
#         try:
#             device = Device.objects.get(id=self.device_id)
#             device.current_coords = coords

#             # Append the new coordinates to the car_history
#             car_history = device.car_history or []
#             car_history.append({
#                 'timestamp': timezone.now().isoformat(),
#                 'coords': coords,
#             })

#             # Limit the car_history to the last 10 entries
#             if len(car_history) > 10:
#                 car_history = car_history[-10:]

#             device.car_history = car_history
#             device.save()

#             return device
#         except Device.DoesNotExist:
#             raise Exception(f"Device with ID {self.device_id} does not exist.")
#         except Exception as e:
#             raise Exception(f"Error updating device coordinates: {e}")

#     @sync_to_async
#     def serialize_device(self, device):
#         """Serialize the device instance."""
#         from .serializers import DeviceSerializer
#         try:
#             serializer = DeviceSerializer(device)
#             return serializer.data
#         except Exception as e:
#             raise Exception(f"Error serializing device: {e}")

#     @sync_to_async
#     def update_websocket_channel_name(self, channel_name):
#         """Update the device's WebSocket channel name in the database."""
#         try:
#             device = Device.objects.get(id=self.device_id)
#             device.websocket_channel_name = channel_name
#             device.save()
#         except Device.DoesNotExist:
#             raise Exception(f"Device with ID {self.device_id} does not exist.")
#         except Exception as e:
#             raise Exception(f"Error updating websocket_channel_name: {e}")

#     @sync_to_async
#     def clear_websocket_channel_name(self):
#         """Clear the device's WebSocket channel name in the database."""
#         try:
#             device = Device.objects.get(id=self.device_id)
#             device.websocket_channel_name = None
#             device.save()
#         except Device.DoesNotExist:
#             raise Exception(f"Device with ID {self.device_id} does not exist.")
#         except Exception as e:
#             raise Exception(f"Error clearing websocket_channel_name: {e}")

#     @sync_to_async
#     def fetch_online_devices(self):
#         """Fetch all online devices."""
#         try:
#             return list(Device.objects.filter(status="online"))
#         except Exception as e:
#             raise Exception(f"Error fetching online devices: {e}")

#     async def update_all_online_devices(self):
#         """Update coordinates for all online devices."""
#         try:
#             online_devices = await self.fetch_online_devices()

#             for device in online_devices:
#                 # Connect to the GPS device
#                 gps_client = await self.initialize_gps_client()

#                 if gps_client:
#                     # Send a command to fetch coordinates (e.g., GET_COORDS#)
#                     command = "GET_COORDS#"
#                     response = await self.send_gps_command(command)

#                     if response:
#                         # Parse the response (e.g., "LAT:37.7749,LON:-122.4194#")
#                         coords = response.strip("#")
#                         await self.update_device_coords(coords)

#                     # Close the TCP connection
#                     gps_client.close()
#         except Exception as e:
#             print(f"Error updating online devices: {e}")