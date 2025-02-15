# utils.py
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import timezone
# for push notification 
from django.core.mail import send_mail
from django.conf import settings
import secrets

def generate_verification_token(user):
    
    timestamp = int(timezone.now().timestamp())
    token = default_token_generator.make_token(user) + f"-{timestamp}"
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    return uid, token

def is_token_valid(user, token):
    """
    Check if the token is valid and has not expired.
    Tokens expire after 15 minutes (900 seconds).
    """
    try:
        # Split the token into the original token and the timestamp
        original_token, timestamp_str = token.rsplit("-", 1)
        timestamp = int(timestamp_str)
    except (ValueError, AttributeError):
        return False

    # Check if the token has expired (15 minutes = 900 seconds)
    if (timezone.now().timestamp() - timestamp) > 900:
        return False

    # Check if the original token is valid
    return default_token_generator.check_token(user, original_token)

# send email notification:
def send_email_notification(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,  # Sender's email
        recipient_list,  # List of recipient emails
        fail_silently=False,  # Raise an exception if email fails
    )
    
def notify_user(user, subject, message):
    """
    Sends a notification to a specific user.
    """
    if user.email:
        send_email_notification(subject, message, [user.email])

def notify_account_users(account, subject, message):
    """
    Sends a notification to all users under an account.
    """
    recipient_list = [user.email for user in account.users.all() if user.email]
    if recipient_list:
        send_email_notification(subject, message, recipient_list)

# reset passwor utility function:
def generate_reset_token():
    return secrets.token_urlsafe(32)  # Generate a secure token

# Decoding JT/T 808 Messages
class JT808Decoder:
    def __init__(self, hex_message):
        self.hex_message = hex_message
        self.decoded_data = {}

    def decode(self):
        # Assuming the hex_message is a valid JT/T 808 hex string
        try:
            # Your JT/T 808 decoding logic
            # Convert hex to bytes
            message_bytes = bytes.fromhex(self.hex_message)
            
            # Extract parts of the message based on the JT/T 808 protocol structure
            # For example, extract coordinates (this is just an example, actual parsing may differ)

            self.decoded_data['coords'] = self.decode_coordinates(message_bytes)

            return self.decoded_data
        except Exception as e:
            raise Exception(f"Error decoding JT/T 808 message: {e}")

    def decode_coordinates(self, message_bytes):
        # Example of extracting coordinates from the message bytes
        lat = int.from_bytes(message_bytes[0:4], byteorder='big') / 1000000  # Example
        lon = int.from_bytes(message_bytes[4:8], byteorder='big') / 1000000  # Example

        return {'latitude': lat, 'longitude': lon}