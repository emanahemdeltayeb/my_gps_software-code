from datetime import timedelta
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import notify_user, notify_account_users

# Create your models here.
# Role/models.py
class Role(models.Model):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('staff', 'Staff'),
    ]
    name = models.CharField(
        choices=ROLE_CHOICES,
        default='customer',
        max_length=255
    )

    def __str__(self):
        return self.name

class Account(models.Model):
    owner = models.ForeignKey('User', on_delete=models.CASCADE, related_name='accounts', null=True, blank=True)
    name = models.CharField(default="Company's Workspace", max_length=100)
    credits = models.PositiveIntegerField(default=0)
    last_credit_reset = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"{self.name}"

    def reset_credits_if_new_year(self):
        now = timezone.now()
        last_reset_year = self.last_credit_reset.year
        current_year = now.year

        if current_year > last_reset_year:
            self.credits = 100
            self.last_credit_reset = now
            self.save()

class User(AbstractUser):
    parent = models.ForeignKey('Account', on_delete=models.CASCADE, related_name='users', null=True, blank=True)  # Parent account only applies if the user is staff or customer, otherwise this is null
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=False)
    STATUS_TYPES = [
        ("active", "Active"),
        ("frozen", "Frozen"),
    ]
    status = models.CharField(max_length=7, choices=STATUS_TYPES, default="active")
    phone_no = models.CharField(max_length=15, blank=True, null=True)
    # for push alarm and notification
    fcm_token = models.CharField(max_length=255, blank=True, null=True)  # Store FCM token

    is_verified = models.BooleanField(default=False) 
    verification_token = models.CharField(max_length=100, blank=True, null=True) 
    verification_token_expiry = models.DateTimeField(null=True, blank=True)  # Token expiry time 

    # Add these fields for password reset
    reset_password_token = models.CharField(max_length=100, blank=True, null=True)
    reset_password_token_expiry = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email

# Driver model   
class Driver(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, related_name="drivers", on_delete=models.CASCADE, null=True)  # Make user field nullable temporarily
    id_number = models.CharField(max_length=255)
    license_number = models.CharField(max_length=50, unique=True)
    license_expire_date = models.DateField()
    contact_number = models.CharField(max_length=15)
    email_address = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    birth_date  = models.DateField()
    join_date = models.DateField() 
    phone_no = models.CharField(max_length=255)
    GENDER_CHOICES = [("Male", "Male"), ("Female", "Female")]
    gender = models.CharField(choices=GENDER_CHOICES, max_length=255,default='Male')

    def __str__(self):
        return self.name
       
# Device (Car) Model
class Device(models.Model):
    device_id = models.CharField(max_length=100,unique=True, null=True, blank=True)
    STATUS_CHOICES = [("online", "Online"), ("offline", "Offline"), ("idle", "Idle")]
    user = models.ForeignKey(User, related_name="devices", on_delete=models.CASCADE)
    status = models.CharField(max_length=7, choices=STATUS_CHOICES, default="offline")
    current_coords = models.CharField(max_length=255)
    car_history = models.JSONField(default=list)
    last_seen = models.DateTimeField(null=True, blank=True)  # Track last time the device updated
    websocket_channel_name = models.CharField(max_length=255, null=True, blank=True)  # Store WebSocket channel name
    total_mileage = models.FloatField(default=0.0)  # Track total mileage
    is_ignition_on = models.BooleanField(default=False)  # Track ignition status
    last_parked_at = models.DateTimeField(null=True, blank=True)  # Track last parking time
    active_driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.CASCADE, related_name='current_driver')
    device_imei = models.CharField(max_length=15, unique=True, null=True, blank=True)
    sim_card_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    sim_card_iccid = models.CharField(max_length=15, unique=True, null=True, blank=True)
    sim_imsi =  models.CharField(max_length=15, unique=True, null=True, blank=True)
    device_model = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Device"
    
    def save(self, *args, **kwargs):
        # Detect ownership change
        is_new_device = self.pk is None
        previous_user = None

        if not is_new_device:
            previous_user = Device.objects.get(pk=self.pk).user

        # Handle credit deduction for a new device or ownership transfer
        if is_new_device or (previous_user and previous_user != self.user):
            account = self.user.parent  # Assuming 'parent' refers to the account model
            if account:
                # Reset credits if it's a new year
                account.reset_credits_if_new_year()
                # Deduct 10 credits for adding or transferring ownership
                if account.credits >= 10:
                    account.credits -= 10
                    account.save()
                else:
                    raise ValueError("Not enough credits to assign this device.")
            else:
                raise ValueError("User does not have an associated account.")

        super().save(*args, **kwargs)

# Signal for Device Status Change Notifications
@receiver(post_save, sender=Device)
def send_device_status_notification(sender, instance, **kwargs):
    user = instance.user
    subject = f"Device Status Update: {instance.status}"
    message = f"""
    Hello {user.username},

    Your device's status has changed:
    - New Status: {instance.status}
    - Last Seen: {instance.last_seen}

    Please check your dashboard for more details.
    """
    notify_user(user, subject, message)

# Alert Model
class Alert(models.Model):
    ALERT_TYPES = [
        ("speeding", "Speeding"),
        ("ignition", "Ignition"),
        ("parking", "Parking"),
        ("idling", "Idling"),
        ("offline", "Offline"),
    ]
    device = models.ForeignKey('Device', on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=10, choices=ALERT_TYPES, default="general")
    message = models.CharField(max_length=255)
    triggered_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    severity = models.CharField(max_length=10, choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")], default="low")

    def __str__(self):
        return f"{self.alert_type.capitalize()} Alert for {self.device.user.username} at {self.triggered_at}"

# Signal for Alert Notifications
@receiver(post_save, sender=Alert)
def send_alert_notification(sender, instance, created, **kwargs):
    if created:  # Send notification only for new alerts
        user = instance.device.user
        subject = f"New Alert: {instance.alert_type}"
        message = f"""
        Hello {user.username},

        You have a new alert:
        - Type: {instance.alert_type}
        - Message: {instance.message}
        - Triggered At: {instance.triggered_at}

        Please check your dashboard for more details.
        """
        notify_user(user, subject, message)
    
# GeoFence Model
class GeoFence(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='geofences')
    name = models.CharField(max_length=255)
    boundary = models.JSONField()  # This can store geofence coordinates (latitude, longitude points)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"GeoFence: {self.name} ({self.boundary})"

# Signal for GeoFence Notifications
@receiver(post_save, sender=GeoFence)
def send_geofence_notification(sender, instance, created, **kwargs):
    if created:  # Send notification only for new geofences
        user = instance.device.user
        subject = f"New GeoFence Created: {instance.name}"
        message = f"""
        Hello {user.username},

        A new geofence has been created:
        - Name: {instance.name}
        - Boundary: {instance.boundary}

        Please check your dashboard for more details.
        """
        notify_user(user, subject, message)

# Trip model to track individual trips:
class Trip(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="trips")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    start_location = models.JSONField()  # { "latitude": x, "longitude": y }
    end_location = models.JSONField(null=True, blank=True)  # { "latitude": x, "longitude": y }
    distance_km = models.FloatField(default=0.0)  # Distance in kilometers
    average_speed_kmh = models.FloatField(default=0.0)  # Average speed in km/h
    max_speed_kmh = models.FloatField(default=0.0)  # Maximum speed in km/h

    def __str__(self):
        return f"Trip for {self.device.user.username} from {self.start_time}"
    
# Signal for Trip Notifications
@receiver(post_save, sender=Trip)
def send_trip_notification(sender, instance, created, **kwargs):
    if created:  # Send notification only for new trips
        user = instance.device.user
        subject = f"New Trip Started"
        message = f"""
        Hello {user.username},

        A new trip has started:
        - Start Time: {instance.start_time}
        - Start Location: {instance.start_location}

        Please check your dashboard for more details.
        """
        notify_user(user, subject, message)

# feedback from the User
class Feedback(models.Model):
    CATEGORY_CHOICES = [
        ('General', 'General'),
        ('Bug', 'Bug'),
        ('Feature Request', 'Feature Request'),
        ('Other', 'Other'),
    ]
    email_address = models.EmailField()
    mobile = models.CharField(max_length=15, blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='General')
    content = models.TextField()  # The main feedback content
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.email_address} on {self.created_at}"