
import socket
import threading
import logging
from django.utils.timezone import now
from api.models import Device
import os


HOST = "0.0.0.0"  # Bind to all interfaces
PORT = 5021  # JT/T 808 listening port

import socket
import threading
import struct
import binascii
from datetime import datetime

def start_tcp_server():
    """
    Start the TCP server for handling JT/T 808 protocol messages.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"TCP Server running on {HOST}:{PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")
        threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()

def handle_client(client_socket):
    try:
        # Send the GET command to the device upon connection
        send_get_command(client_socket)
        
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Received raw data: {binascii.hexlify(data).decode()}")

            decoded_data = decode_payload(data)
            if decoded_data:
                print(f"Decoded Data: {decoded_data}")

            imei = extract_imei(data)
            if imei:
                device_id = generate_device_id(imei)
                register_or_update_device(device_id)
                print(f"Device {device_id} registered.")

            # Send registration acknowledgment
            send_registration_ack(client_socket)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def send_get_command(client_socket):
    """
    Send the GET command to check the current GPS device settings.
    """
    try:
        command = "GET,IMEI,MIP,APN,PROTOCOL,RSSI#"
        client_socket.send(command.encode('utf-8'))
        print(f"Sent command: {command}")
    except Exception as e:
        print(f"Error sending GET command: {e}")

def send_registration_ack(client_socket):
    """
    Send registration packet reply according to the JT/T 808 protocol.
    """
    try:
        # Example acknowledgment packet (adjust based on protocol specifics)
        ack_packet = b'\x7E\x80\x01\x00\x00\x00\x00\x00\x00\x7E'
        client_socket.send(ack_packet)
        print("Sent registration acknowledgment.")
    except Exception as e:
        print(f"Error sending registration acknowledgment: {e}")

def decode_payload(payload):
    """
    Decode the payload data from hexadecimal to human-readable values.
    """
    decoded_info = {}

    try:
        imei_bytes = payload[4:19]
        imei = ''.join(f"{b:02X}" for b in imei_bytes)
        decoded_info["imei"] = imei

        latitude_bytes = payload[19:23]
        longitude_bytes = payload[23:27]
        latitude = struct.unpack('>I', latitude_bytes)[0] / 1000000
        longitude = struct.unpack('>I', longitude_bytes)[0] / 1000000
        decoded_info["latitude"] = latitude
        decoded_info["longitude"] = longitude

        speed_bytes = payload[27:28]
        timestamp_bytes = payload[28:32]
        speed = int.from_bytes(speed_bytes, byteorder='big')
        timestamp = struct.unpack('>I', timestamp_bytes)[0]
        decoded_info["speed"] = speed
        decoded_info["timestamp"] = timestamp
    except Exception as e:
        print(f"Error decoding payload: {e}")
    
    return decoded_info

def extract_imei(data):
    """
    Extract IMEI from JT/T 808 message payload.
    """
    try:
        imei_bytes = data[4:19]
        imei = ''.join(f"{b:02X}" for b in imei_bytes)
        return imei if len(imei) == 15 else None
    except Exception as e:
        print(f"Error extracting IMEI: {e}")
        return None

def generate_device_id(imei):
    """
    Generate device ID as "1" + last 10 digits of IMEI, optionally adding a leading zero.
    """
    last_10_digits = imei[-10:]
    device_id = f"1{last_10_digits}"
    if should_prepend_zero(device_id):
        device_id = '0' + device_id
    return device_id

def should_prepend_zero(device_id):
    """
    Decide whether to prepend a zero to the device ID.
    """
    return device_id.startswith('1')

def register_or_update_device(device_id):
    """
    Register or update the device in the database.
    """
    try:
        # Simulated database logic (replace with actual DB call)
        print(f"Device {device_id} registered or updated at {datetime.now()}")
    except Exception as e:
        print(f"Error registering/updating device: {e}")


# import struct
# import binascii

# HOST = "0.0.0.0"  # Bind to all interfaces
# PORT = 5021  # JT/T 808 listening port

# def start_tcp_server():
#     """
#     Start the TCP server for handling JT/T 808 protocol messages.
#     """
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.bind((HOST, PORT))
#     server_socket.listen(5)
#     print(f"TCP Server running on {HOST}:{PORT}")

#     while True:
#         client_socket, client_address = server_socket.accept()
#         print(f"Connection from {client_address}")
#         threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()

# def handle_client(client_socket):
#     try:
#         while True:
#             data = client_socket.recv(1024)
#             if not data:
#                 break
#             print(f"Received raw data: {binascii.hexlify(data).decode()}")

#             # Decode payload into human-readable data
#             decoded_data = decode_payload(data)
#             if decoded_data:
#                 print(f"Decoded Data: {decoded_data}")

#             imei = extract_imei(data)
#             if imei:
#                 device_id = generate_device_id(imei)
#                 register_or_update_device(device_id)
#                 print(f"Device {device_id} registered.")

#             # Send response to the client
#             client_socket.send(b'\x7E\x00\x00\x00\x00\x00\x00\x00\x7E')
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         client_socket.close()

# def decode_payload(payload):
#     """
#     Decode the payload data from hexadecimal to human-readable values.
#     """
#     decoded_info = {}

#     try:
#         # Example extraction: Assume IMEI is the first 15 bytes
#         imei_bytes = payload[4:19]  # Adjust based on your protocol
#         imei = ''.join(f"{b:02X}" for b in imei_bytes)
#         decoded_info["imei"] = imei

#         # Example extraction: Assume latitude and longitude are 4 bytes each
#         latitude_bytes = payload[19:23]
#         longitude_bytes = payload[23:27]
#         latitude = struct.unpack('>I', latitude_bytes)[0] / 1000000  # Example scaling
#         longitude = struct.unpack('>I', longitude_bytes)[0] / 1000000
#         decoded_info["latitude"] = latitude
#         decoded_info["longitude"] = longitude

#         # Example extraction: Speed (1 byte) and timestamp (4 bytes)
#         speed_bytes = payload[27:28]
#         timestamp_bytes = payload[28:32]
#         speed = int.from_bytes(speed_bytes, byteorder='big')
#         timestamp = struct.unpack('>I', timestamp_bytes)[0]  # Example conversion
#         decoded_info["speed"] = speed
#         decoded_info["timestamp"] = timestamp
#     except Exception as e:
#         print(f"Error decoding payload: {e}")
    
#     return decoded_info

# def extract_imei(data):
#     """
#     Extract IMEI from JT/T 808 message payload.
#     """
#     try:
#         imei_bytes = data[4:19]  # Assuming IMEI is 15 bytes at offset 4
#         imei = ''.join(f"{b:02X}" for b in imei_bytes)
#         return imei if len(imei) == 15 else None
#     except Exception as e:
#         print(f"Error extracting IMEI: {e}")
#         return None

# def generate_device_id(imei):
#     """
#     Generate device ID as "1" + last 10 digits of IMEI.
#     Optionally add a leading zero depending on platform logic.
#     """
#     last_10_digits = imei[-10:]  # Get the last 10 digits of the IMEI
#     device_id = f"1{last_10_digits}"  # Concatenate '1' + last 10 digits of IMEI
    
#     # Platform logic to prepend '0' if necessary
#     if should_prepend_zero(device_id):
#         device_id = '0' + device_id  # Prepend a zero if needed
    
#     return device_id

# def should_prepend_zero(device_id):
#     """
#     Platform logic to decide whether to prepend a zero to the device ID.
#     In this example, we simply check if the first character is '1' and prepend '0' if true.
#     Modify this function based on your platform logic.
#     """
#     # Example: Add 0 if the device ID starts with '1'
#     return device_id.startswith('1')

# def register_or_update_device(device_id):
#     """
#     Register or update the device in the database.
#     """
#     try:
#         device, created = Device.objects.get_or_create(device_id=device_id)
#         device.last_connected = now()
#         device.save()
#         action = "Registered" if created else "Updated"
#         print(f"{action} device: {device_id}")
#     except Exception as e:
#         print(f"Error registering/updating device: {e}")

# # Function to send the GET command to the GPS device
# def send_get_command(client_socket):
#     try:
#         # Command to check the current setting
#         command = "GET,IMEI,MIP,APN,PROTOCOL,RSSI#"
#         # Encode the command to bytes and send it to the client device
#         client_socket.send(command.encode('utf-8'))
#         print(f"Sent command: {command}")
#     except Exception as e:
#         print(f"Error sending GET command: {e}")

# 206-02-2025 second one work fine: 
##################################
# HOST = "0.0.0.0"  # Bind to all interfaces
# PORT = 5021  # JT/T 808 listening port

# def start_tcp_server():
#     """
#     Start the TCP server for handling JT/T 808 protocol messages.
#     """
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.bind((HOST, PORT))
#     server_socket.listen(5)
#     print(f"TCP Server running on {HOST}:{PORT}")

#     while True:
#         client_socket, client_address = server_socket.accept()
#         print(f"Connection from {client_address}")
#         threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()

# def handle_client(client_socket):
#     try:
#         while True:
#             data = client_socket.recv(1024)
#             if not data:
#                 break
#             imei = extract_imei(data)
#             if imei:
#                 device_id = generate_device_id(imei)
#                 register_or_update_device(device_id)
#                 print(f"Device {device_id} registered.")
#                 client_socket.send(b'\x7E\x00\x00\x00\x00\x00\x00\x00\x7E')
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         client_socket.close()

# def extract_imei(data):
#     """
#     Extract IMEI from JT/T 808 message payload.
#     """
#     try:
#         # Example extraction assuming IMEI is 15 bytes at offset 4
#         imei_bytes = data[4:19]
#         imei = ''.join(f"{b:02X}" for b in imei_bytes)
#         return imei if len(imei) == 15 else None
#     except Exception as e:
#         print(f"Error extracting IMEI: {e}")
#         return None

# def generate_device_id(imei):
#     """
#     Generate device ID as "1" + last 10 digits of IMEI.
#     Optionally add a leading zero depending on platform logic.
#     """
#     last_10_digits = imei[-10:]  # Get the last 10 digits of the IMEI
#     device_id = f"1{last_10_digits}"  # Concatenate '1' + last 10 digits of IMEI
    
#     # Platform logic to prepend '0' if necessary
#     if should_prepend_zero(device_id):
#         device_id = '0' + device_id  # Prepend a zero if needed
    
#     return device_id

# def should_prepend_zero(device_id):
#     """
#     Platform logic to decide whether to prepend a zero to the device ID.
#     In this example, we simply check if the first character is '1' and prepend '0' if true.
#     Modify this function based on your platform logic.
#     """
#     # Example: Add 0 if the device ID starts with '1'
#     return device_id.startswith('1')

# def register_or_update_device(device_id):
#     """
#     Register or update the device in the database.
#     """
#     try:
#         device, created = Device.objects.get_or_create(device_id=device_id)
#         device.last_connected = now()
#         device.save()
#         action = "Registered" if created else "Updated"
#         print(f"{action} device: {device_id}")
#     except Exception as e:
#         print(f"Error registering/updating device: {e}")

# import socket
# import threading

# # Function to send the GET command to the GPS device
# def send_get_command(client_socket):
#     try:
#         # Command to check the current setting
#         command = "GET,IMEI,MIP,APN,PROTOCOL,RSSI#"
#         # Encode the command to bytes and send it to the client device
#         client_socket.send(command.encode('utf-8'))
#         print(f"Sent command: {command}")
#     except Exception as e:
#         print(f"Error sending GET command: {e}")

# # Handle the client interaction
# def handle_client(client_socket):
#     try:
#         while True:
#             data = client_socket.recv(1024)
#             if not data:
#                 break
#             print(f"Received data: {data}")
            
#             # Extract IMEI or other necessary details as needed
#             imei = extract_imei(data)
#             if imei:
#                 device_id = generate_device_id(imei)
#                 register_or_update_device(device_id)
#                 print(f"Device {device_id} registered.")

#             # Send the command to the device
#             send_get_command(client_socket)

#             # Respond back to the client (optional, depending on protocol)
#             client_socket.send(b'\x7E\x00\x00\x00\x00\x00\x00\x00\x7E')
            
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         client_socket.close()

# # Example of extracting IMEI and generating the device ID
# def extract_imei(data):
#     try:
#         imei_bytes = data[4:19]  # Assuming IMEI is 15 bytes at position 4
#         imei = ''.join(f"{b:02X}" for b in imei_bytes)
#         return imei if len(imei) == 15 else None
#     except Exception as e:
#         print(f"Error extracting IMEI: {e}")
#         return None

# def generate_device_id(imei):
#     return f"1{imei[-10:]}"

# def register_or_update_device(device_id):
#     print(f"Device {device_id} registered or updated.")
#######################################################



# 206-02-2025 first one 

#  # Configure logging
# # Ensure the logs directory exists
# os.makedirs('logs', exist_ok=True)

# # Configure logging to write only to a file
# logging.basicConfig(
#     level=logging.INFO,  # Change this to logging.DEBUG for more detailed logs
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('logs/tcp_server.log'),  # Log to a file in the 'logs' folder
#     ]
# )
# HOST = "0.0.0.0"  # Bind to all interfaces
# PORT = 5021  # JT/T 808 listening port

# def start_tcp_server():
#     """
#     Start the TCP server for handling JT/T 808 protocol messages.
#     """
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.bind((HOST, PORT))
#     server_socket.listen(5)
#     print(f"TCP Server running on {HOST}:{PORT}")

#     while True:
#         client_socket, client_address = server_socket.accept()
#         print(f"Connection from {client_address}")
#         threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()

# def handle_client(client_socket):
#     try:
#         while True:
#             data = client_socket.recv(1024)
#             if not data:
#                 break
#             imei = extract_imei(data)
#             if imei:
#                 device_id = generate_device_id(imei)
#                 register_or_update_device(device_id)
#                 print(f"Device {device_id} registered.")
#                 client_socket.send(b'\x7E\x00\x00\x00\x00\x00\x00\x00\x7E')
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         client_socket.close()

# def extract_imei(data):
#     """
#     Extract IMEI from JT/T 808 message payload.
#     """
#     try:
#         # Example extraction assuming IMEI is 15 bytes at offset 4
#         imei_bytes = data[4:19]
#         imei = ''.join(f"{b:02X}" for b in imei_bytes)
#         return imei if len(imei) == 15 else None
#     except Exception as e:
#         print(f"Error extracting IMEI: {e}")
#         return None

# def generate_device_id(imei):
#     """
#     Generate device ID as "1" + last 10 digits of IMEI.
#     """
#     return f"1{imei[-10:]}"

# def register_or_update_device(device_id):
#     """
#     Register or update the device in the database.
#     """
#     try:
#         device, created = Device.objects.get_or_create(device_id=device_id)
#         device.last_connected = now()
#         device.save()
#         action = "Registered" if created else "Updated"
#         print(f"{action} device: {device_id}")
#     except Exception as e:
#         print(f"Error registering/updating device: {e}")
# def start_tcp_server():
#     """
#     Start the TCP server for handling JT/T 808 protocol messages.
#     """
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.bind((HOST, PORT))
#     server_socket.listen(5)
#     logging.info(f"TCP Server running on {HOST}:{PORT}")

#     while True:
#         client_socket, client_address = server_socket.accept()
#         logging.info(f"Connection from {client_address}")
#         threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()

# def handle_client(client_socket):
#     try:
#         while True:
#             data = client_socket.recv(1024)
#             if not data:
#                 break
#             imei = extract_imei(data)
#             if imei:
#                 device_id = generate_device_id(imei)
#                 register_or_update_device(device_id)
#                 logging.info(f"Device {device_id} registered.")
#                 client_socket.send(b'\x7E\x00\x00\x00\x00\x00\x00\x00\x7E')
#     except Exception as e:
#         logging.error(f"Error handling client: {e}")
#     finally:
#         client_socket.close()

# def extract_imei(data):
#     """
#     Extract IMEI from JT/T 808 message payload.
#     """
#     try:
#         # Example extraction assuming IMEI is 15 bytes at offset 4
#         imei_bytes = data[4:19]
#         imei = ''.join(f"{b:02X}" for b in imei_bytes)
#         return imei if len(imei) == 15 else None
#     except Exception as e:
#         logging.error(f"Error extracting IMEI: {e}")
#         return None

# def generate_device_id(imei):
#     """
#     Generate device ID as "1" + last 10 digits of IMEI.
#     """
#     return f"1{imei[-10:]}"

# def register_or_update_device(device_id):
#     """
#     Register or update the device in the database.
#     """
#     try:
#         device, created = Device.objects.get_or_create(device_id=device_id)
#         device.last_connected = now()
#         device.save()
#         action = "Registered" if created else "Updated"
#         logging.info(f"{action} device: {device_id}")
#     except Exception as e:
#         logging.error(f"Error registering/updating device: {e}")

# import socket
# import threading
# from django.utils.timezone import now
# from api.models import Device

# HOST = "0.0.0.0"  # Bind to all interfaces
# PORT = 5021  # JT/T 808 listening port

# def start_tcp_server():
#     """
#     Start the TCP server for handling JT/T 808 protocol messages.
#     """
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.bind((HOST, PORT))
#     server_socket.listen(5)
#     print(f"TCP Server running on {HOST}:{PORT}")

#     while True:
#         client_socket, client_address = server_socket.accept()
#         print(f"Connection from {client_address}")
#         threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()

# def handle_client(client_socket):
#     try:
#         while True:
#             data = client_socket.recv(1024)
#             if not data:
#                 break
#             imei = extract_imei(data)
#             if imei:
#                 device_id = generate_device_id(imei)
#                 register_or_update_device(device_id)
#                 print(f"Device {device_id} registered.")
#                 client_socket.send(b'\x7E\x00\x00\x00\x00\x00\x00\x00\x7E')
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         client_socket.close()

# def extract_imei(data):
#     """
#     Extract IMEI from JT/T 808 message payload.
#     """
#     try:
#         # Example extraction assuming IMEI is 15 bytes at offset 4
#         imei_bytes = data[4:19]
#         imei = ''.join(f"{b:02X}" for b in imei_bytes)
#         return imei if len(imei) == 15 else None
#     except Exception as e:
#         print(f"Error extracting IMEI: {e}")
#         return None

# def generate_device_id(imei):
#     """
#     Generate device ID as "1" + last 10 digits of IMEI.
#     """
#     return f"1{imei[-10:]}"

# def register_or_update_device(device_id):
#     """
#     Register or update the device in the database.
#     """
#     try:
#         device, created = Device.objects.get_or_create(device_id=device_id)
#         device.last_connected = now()
#         device.save()
#         action = "Registered" if created else "Updated"
#         print(f"{action} device: {device_id}")
#     except Exception as e:
#         print(f"Error registering/updating device: {e}")