# firebase.py
import firebase_admin # type: ignore
from firebase_admin import credentials, messaging

# Initialize Firebase
# cred = credentials.Certificate("path/to/your/firebase-service-account-key.json")
cred = credentials.Certificate("core/firebase/gps-tracking-software-d9e97-firebase-adminsdk-c8t67-ffeed180ea.json")
firebase_admin.initialize_app(cred)

def send_push_notification(fcm_token, title, body):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=fcm_token,
    )
    try:
        messaging.send(message)
        print("Notification sent successfully.")
    except Exception as e:
        print(f"Error sending notification: {e}")