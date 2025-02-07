import logging

from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model, login
from django.contrib.auth.models import User 
from django.utils.encoding import force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ObjectDoesNotExist

from .models import Account, User, Device, Alert, GeoFence, Trip, Driver, Role, Feedback
from .serializers import DeviceSerializer, AlertSerializer, GeoFenceSerializer, UserSerializer, AccountSerializer,TripSerializer, FeedbackSerializer
from .utils import generate_verification_token, is_token_valid
from .permissions import IsAccountOwner, IsUserOwner, IsDeviceOwner, IsAlertOwner, IsGeoFenceOwner, IsOwnerOrDevice, IsDriverOwner
from django.shortcuts import get_object_or_404, render
from collections import defaultdict
from django.utils import timezone
from .serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from .utils import generate_reset_token  # You need to implement this utility function
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import csv
from io import StringIO
from rest_framework.viewsets import ModelViewSet
from .serializers import DriverSerializer

# Create your views here.
# Device Management View (CRUD)
class DeviceViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceSerializer
    permission_classes = [IsDeviceOwner,IsAuthenticated, IsUserOwner]  # Only device owners can access

    def get_queryset(self):
        # Only return devices owned by the logged-in user
        return Device.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically set the user to the logged-in user
        serializer.save(user=self.request.user)
        
# Alerts Managment View CRUD
class AlertViewSet(viewsets.ModelViewSet):
    serializer_class = AlertSerializer
    permission_classes = [IsAlertOwner,IsAuthenticated]  # Only alert owners can access

    def get_queryset(self):
        # Only return alerts for devices owned by the logged-in user
        return Alert.objects.filter(device__user=self.request.user)
    
#  GeoFence Managment View CRUD 
class GeoFenceViewSet(viewsets.ModelViewSet):
    serializer_class = GeoFenceSerializer
    permission_classes = [IsGeoFenceOwner,IsAuthenticated]  # Only geofence owners can access

    def get_queryset(self):
        # Only return geofences for devices owned by the logged-in user
        return GeoFence.objects.filter(device__user=self.request.user)

class TripViewSet(viewsets.ModelViewSet):
    serializer_class = TripSerializer
    permission_classes = [IsOwnerOrDevice,IsAuthenticated]  # Only device owners can access
    def get_queryset(self):
        # Only return geofences for devices owned by the logged-in user
        return Trip.objects.filter(device__user=self.request.user)

class DriverViewSet(ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated, IsDriverOwner]

    def get_queryset(self):
        # Filter drivers for the current user's devices or account
        return Driver.objects.filter(user=self.request.user)

class TripViewSet(ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated, IsDriverOwner]

    def get_queryset(self):
        # Filter drivers for the current user's devices or account
        return Driver.objects.filter(user=self.request.user)
    
class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated, IsDriverOwner]

    def get_queryset(self):
        # Filter drivers for the current user's devices or account
        return Driver.objects.filter(user=self.request.user)

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAccountOwner]  # Only account owners can access

    def get_queryset(self):
        # Only return end users owned by the logged-in account
        return User.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Check if the logged-in account is a reseller
        if self.request.user.type != Account.RESELLER:
            raise PermissionDenied("Only reseller accounts can create new end users.")

        # Automatically set the owner to the logged-in account
        serializer.save(owner=self.request.user)

class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # Save the account
            user = serializer.save()

            # Generate verification token
            uid, token = generate_verification_token(user)

            # Save the token in the Account model
            user.verification_token = token
            user.save()  # Save the token to the database

            # Send verification email
            verification_link = f"http://127.0.0.1:8000/api/verify-email/{uid}/{token}/"
            subject = 'Verify Your Email'
            message = render_to_string('auth/verification_email.html', {
                'user': user,
                'verification_link': verification_link,
            })
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
# Account Managment View CRUD
class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated,IsAccountOwner]

    def get_queryset(self):
        # Only return the logged-in Account
        return Account.objects.filter(id=self.request.user.id)

class AccountRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            # Save the account
            account = serializer.save()

            # Generate verification token
            uid, token = generate_verification_token(account)

            # Save the token in the Account model
            account.verification_token = token
            account.save()  # Save the token to the database

            # Send verification email
            verification_link = f"http://127.0.0.1:8000/api/verify-email/{uid}/{token}/"
            subject = 'Verify Your Email'
            message = render_to_string('auth/verification_email.html', {
                'user': account,
                'verification_link': verification_link,
            })
            send_mail(subject, message, settings.EMAIL_HOST_USER, [account.email])

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
User = get_user_model()

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and is_token_valid(user, token):
            user.is_verified = True
            user.verification_token = token
            user.save()

        if user.owner:
            user.owner.is_verified = True
            # user.owner.verification_token = token  # Save the token in the Account model
            user.owner.save()
            return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid or expired verification link."}, status=status.HTTP_400_BAD_REQUEST)

logger = logging.getLogger(__name__)

# Login API View
class LoginAPIView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to access this endpoint

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        # Input validation
        if not username or not password:
            return Response({'detail': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Log the login attempt
        logger.info(f"Login attempt with username: {username}")

        try:
            # Fetch the user by username
            user = User.objects.get(username=username)

            # Compare plain-text passwords (INSECURE - DO NOT USE IN PRODUCTION)
            if user.password == password:  # Plain-text comparison
                logger.info(f"User authenticated: {user}")

                # Log the user in (session-based authentication)
                login(request, user)

                return Response({
                    'detail': 'Login successful',
                    'user_id': user.id,
                    'username': user.username,
                }, status=status.HTTP_200_OK)
            else:
                logger.warning("Invalid password")
                return Response({'detail': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)

        except ObjectDoesNotExist:
            logger.warning("Invalid username")
            return Response({'detail': 'Invalid username'}, status=status.HTTP_401_UNAUTHORIZED)

# Logout API View  
class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AddNewUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the authenticated User
        logged_in_User = request.user

        # Get the Account owner of the logged-in User
        account_owner = logged_in_User.owner

        # Ensure the authenticated User has an Account owner
        if not isinstance(account_owner, Account):
            return Response({"error": "The logged-in User must have an Account owner."}, status=status.HTTP_403_FORBIDDEN)

        # Check if the logged-in account is a reseller
        if logged_in_User.owner.type != Account.RESELLER:
            return Response(
                {"error": "Only reseller accounts can add new end users."},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        # Validate the input data
        serializer = UserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Create the new User
            new_User = serializer.save(owner=account_owner)

            # Generate verification token for the new User
            uid, token = generate_verification_token(new_User)
            new_User.verification_token = token
            new_User.save()

            # Send verification email to the new User's email
            verification_link = f"http://127.0.0.1:8000/api/verify-email/{uid}/{token}/"
            subject = 'Verify Your Email'
            message = render_to_string('auth/verification_email.html', {
                'user': new_User,
                'verification_link': verification_link,
            })
            send_mail(subject, message, settings.EMAIL_HOST_USER, [new_User.email])

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# All Reports Views:
# integrated function for export pdf and csv
class BaseReportView(APIView):
    permission_classes = [IsAuthenticated]

    def export_pdf(self, request, template, context, filename):
        template = get_template(template)
        html = template.render(context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response

    def export_csv(self, data, filename):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        writer = csv.writer(response)
        writer.writerow(data[0].keys())
        for row in data:
            writer.writerow(row.values())
        return response

    def get(self, request):
        export_type = request.GET.get('export', None)
        context = self.get_context(request)
        if export_type == 'pdf':
            return self.export_pdf(request, self.template, context, self.filename)
        elif export_type == 'csv':
            return self.export_csv(context[self.context_key], f"{self.filename}")
        return render(request, self.template, context)

# MotionOverviewReport
class MotionOverviewReport(BaseReportView):
    template = 'reports/motion_overview.html'
    filename = 'motion_overview_report'
    context_key = 'motion_data'

    def get_context(self, request):
        user = request.user
        devices = Device.objects.filter(user=user)
        motion_data = {
            "online": devices.filter(status="online").count(),
            "offline": devices.filter(status="offline").count(),
            "idle": devices.filter(status="idle").count(),
        }
        return {self.context_key: [motion_data]}

# MileageReport
class MileageReport(BaseReportView):
    template = 'reports/mileage_report.html'
    filename = 'mileage_report'
    context_key = 'daily_mileage'

    def get_context(self, request):
        user = request.user
        devices = Device.objects.filter(user=user)
        total_mileage = sum(device.total_mileage for device in devices)
        daily_mileage = defaultdict(float)
        for device in devices:
            trips = Trip.objects.filter(device=device)
            for trip in trips:
                date = trip.start_time.date()
                daily_mileage[date] += trip.distance_km
        return {
            'total_mileage': total_mileage,
            self.context_key: [{"date": k, "mileage": v} for k, v in daily_mileage.items()],
        }

# DailyParkingReport
class DailyParkingReport(BaseReportView):
    template = 'reports/daily_parking_report.html'
    filename = 'daily_parking_report'
    context_key = 'parking_data'

    def get_context(self, request):
        user = request.user
        devices = Device.objects.filter(user=user)
        parking_data = []
        for device in devices:
            if device.last_parked_at:
                parking_data.append({
                    "device": device.id,
                    "last_parked_at": device.last_parked_at,
                    "location": device.current_coords,
                })
        return {self.context_key: parking_data}

# IdlingReport
class IdlingReport(BaseReportView):
    template = 'reports/idling_report.html'
    filename = 'idling_report'
    context_key = 'idling_data'

    def get_context(self, request):
        user = request.user
        devices = Device.objects.filter(user=user)
        idling_data = []
        for device in devices:
            idling_events = device.car_history.filter(status="idle")
            for event in idling_events:
                idling_data.append({
                    "device": device.id,
                    "timestamp": event["timestamp"],
                    "duration_minutes": event.get("duration_minutes", 0),
                })
        return {self.context_key: idling_data}

# IgnitionReport
class IgnitionReport(BaseReportView):
    template = 'reports/ignition_report.html'
    filename = 'ignition_report'
    context_key = 'ignition_data'

    def get_context(self, request):
        user = request.user
        devices = Device.objects.filter(user=user)
        ignition_data = []
        for device in devices:
            ignition_events = device.car_history.filter(is_ignition_on=True)
            for event in ignition_events:
                ignition_data.append({
                    "device": device.id,
                    "timestamp": event["timestamp"],
                    "status": "on" if event["is_ignition_on"] else "off",
                })
        return {self.context_key: ignition_data}

# OfflineReport
class OfflineReport(BaseReportView):
    template = 'reports/offline_report.html'
    filename = 'offline_report'
    context_key = 'offline_data'

    def get_context(self, request):
        user = request.user
        devices = Device.objects.filter(user=user)
        offline_data = []
        for device in devices:
            offline_events = device.car_history.filter(status="offline")
            for event in offline_events:
                offline_data.append({
                    "device": device.id,
                    "timestamp": event["timestamp"],
                    "duration_minutes": event.get("duration_minutes", 0),
                })
        return {self.context_key: offline_data}

# TripReport
class TripReport(BaseReportView):
    template = 'reports/trip_report.html'
    filename = 'trip_report'
    context_key = 'trip_data'

    def get_context(self, request):
        user = request.user
        trips = Trip.objects.filter(device__user=user)
        trip_data = []
        for trip in trips:
            trip_data.append({
                "start_time": trip.start_time,
                "end_time": trip.end_time,
                "distance_km": trip.distance_km,
                "average_speed_kmh": trip.average_speed_kmh,
                "max_speed_kmh": trip.max_speed_kmh,
            })
        return {self.context_key: trip_data}

# SpeedingReport
class SpeedingReport(BaseReportView):
    template = 'reports/speeding_report.html'
    filename = 'speeding_report'
    context_key = 'speeding_data'

    def get_context(self, request):
        user = request.user
        speeding_alerts = Alert.objects.filter(device__user=user, alert_type="speeding")
        speeding_data = []
        for alert in speeding_alerts:
            speeding_data.append({
                "timestamp": alert.triggered_at,
                "speed_kmh": alert.message,  # Assuming message contains speed
            })
        return {self.context_key: speeding_data}

# AlertOverviewReport
class AlertOverviewReport(BaseReportView):
    template = 'reports/alert_overview.html'
    filename = 'alert_overview_report'
    context_key = 'alert_summary'

    def get_context(self, request):
        user = request.user
        alerts = Alert.objects.filter(device__user=user)
        alert_summary = defaultdict(int)
        for alert in alerts:
            alert_summary[alert.alert_type] += 1
        return {self.context_key: [{"alert_type": k, "count": v} for k, v in alert_summary.items()]}

# DeviceAlertReport
class DeviceAlertReport(BaseReportView):
    template = 'reports/device_alert_report.html'
    filename = 'device_alert_report'
    context_key = 'alerts'

    def get_context(self, request):
        user = request.user
        alerts = Alert.objects.filter(device__user=user)
        return {self.context_key: list(alerts.values())}

# AlertDetailReport
class AlertDetailReport(BaseReportView):
    template = 'reports/alert_detail.html'
    filename = 'alert_detail_report'
    context_key = 'alert'

    def get_context(self, request, alert_id):
        user = request.user
        alert = Alert.objects.filter(id=alert_id, device__user=user).first()
        if not alert:
            return {'error': 'Alert not found'}
        return {self.context_key: [alert]}
    
# Password Reset views
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            # Check if the email belongs to a User
            user = User.objects.filter(email=email).first()

            if user:
                # Generate a reset token for the User
                user.reset_password_token = generate_reset_token()
                user.reset_password_token_expiry = timezone.now() + timezone.timedelta(hours=1)
                user.save()

                # Send reset email
                reset_link = f"http://127.0.0.1:8000/api/reset-password/{user.reset_password_token}/"
                subject = 'Password Reset Request'
                message = render_to_string('auth/password_reset_email.html', {
                    'reset_link': reset_link,
                })
                send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

                return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No user found with this email."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']

            # Check if the token belongs to a User
            user = User.objects.filter(reset_password_token=token).first()

            if user:
                # Check if the token is expired
                if user.reset_password_token_expiry < timezone.now():
                    return Response({"error": "Token has expired."}, status=status.HTTP_400_BAD_REQUEST)

                # Update the password and clear the reset token
                user.set_password(new_password)  # Use set_password to hash the password
                user.reset_password_token = None
                user.reset_password_token_expiry = None
                user.save()

                return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# trip model view:
class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrDevice]

    def get_queryset(self):
        # Filter trips to only include those belonging to the user's devices
        user = self.request.user
        return Trip.objects.filter(device__user=user)

class FeedbackCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        # Create a new feedback instance using the submitted data
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            feedback = serializer.save()  # Save the feedback
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)