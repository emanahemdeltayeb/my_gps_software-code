from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from datetime import timedelta
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from django.utils import timezone
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from .models import Device, Alert

def send_email_notification(subject, message, recipient_list):
    """
    Sends an email notification.
    """
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,  # Sender's email
        recipient_list,  # List of recipient emails
        fail_silently=False,  # Raise an exception if email fails
    )

def check_alert_conditions(device):
    """
    Checks for alert conditions and sends email notifications if conditions are met.
    """
    user = device.user

    # Example: Check if the device is offline
    if device.status == "offline":
        subject = "Device Offline"
        message = f"""
        Hello {user.username},

        Your device {device.id} is offline.
        - Last Seen: {device.last_seen}

        Please check your dashboard for more details.
        """
        send_email_notification(subject, message, [user.email])

def save_car_coordinates():
    """
    Saves car coordinates to cache and checks for alert conditions.
    """
    # Get all online devices
    online_devices = Device.objects.filter(status="online")

    for device in online_devices:
        # Simulate updating coordinates (replace with actual logic)
        new_coords = "37.7749,-122.4194"  # Example coordinates
        timestamp = timezone.now().isoformat()

        # Get the cached history for the device
        cache_key = f"device_{device.id}_history"
        history = cache.get(cache_key, [])

        # Append new coordinates to the cached history
        history.append({"coords": new_coords, "timestamp": timestamp})

        # Limit the history to the last 10 entries
        if len(history) > 10:
            history = history[-10:]

        # Update the cache
        cache.set(cache_key, history)

        # Send WebSocket update for each device
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"device_{device.id}",
            {
                "type": "device_message",
                "message": {
                    "coords": new_coords,
                    "timestamp": timestamp,
                },
            },
        )

        # Check for alert conditions and send email notifications
        check_alert_conditions(device)

def save_daily_history():
    """
    Saves cached history to the database for all online devices.
    """
    # Get the cached history for all devices
    cache_key = "all_devices_history"
    history = cache.get(cache_key, {})

    if history:
        # Save the cached history to the database for each online device
        for device_id, device_history in history.items():
            device = Device.objects.filter(id=device_id, status="online").first()
            if device:
                # Append the cached history to the database
                device.car_history.extend(device_history)

                # Limit the car_history to the last 10 entries
                if len(device.car_history) > 10:
                    device.car_history = device.car_history[-10:]

                device.save()

        # Clear the cache
        cache.delete(cache_key)

def cleanup_old_car_history():
    """
    Cleans up old car history for all online devices.
    """
    # Calculate the date 30 days ago
    thirty_days_ago = timezone.now() - timedelta(days=30)

    # Fetch all online devices
    online_devices = Device.objects.filter(status="online")

    for device in online_devices:
        # Filter out history entries older than 30 days
        device.car_history = [
            entry for entry in device.car_history
            if timezone.datetime.fromisoformat(entry["timestamp"]) > thirty_days_ago
        ]
        device.save()

def start_scheduler():
    """
    Starts the scheduler with predefined jobs.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Save coordinates to cache for all online devices every 2 seconds
    scheduler.add_job(
        save_car_coordinates,
        trigger=IntervalTrigger(seconds=2),
        id="save_car_coordinates",
        max_instances=1,
        replace_existing=True,
    )

    # Save cached history to database for all online devices once a day at midnight
    scheduler.add_job(
        save_daily_history,
        trigger=CronTrigger(hour=0, minute=0),  # Midnight
        id="save_daily_history",
        max_instances=1,
        replace_existing=True,
    )

    # Clean up old car history for all online devices every 30 days
    scheduler.add_job(
        cleanup_old_car_history,
        trigger=IntervalTrigger(days=30),  # Every 30 days
        id="cleanup_old_car_history",
        max_instances=1,
        replace_existing=True,
    )

    scheduler.start()

from .tcp_server import start_tcp_server

def start_scheduler():
    """
    Start the TCP server in the background.
    """
    print("Starting TCP server...")
    start_tcp_server()
