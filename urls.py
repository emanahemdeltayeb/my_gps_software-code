from django.urls import path, include
from .views import ( LogoutView, DeviceViewSet,AlertViewSet,GeoFenceViewSet,UserViewSet,AccountViewSet, VerifyEmailView, 
                    AddNewUserView,UserRegisterView, DriverViewSet, TripViewSet, RoleViewSet, FeedbackCreateView)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from .views import ( MotionOverviewReport, MileageReport, DailyParkingReport, IdlingReport, IgnitionReport, OfflineReport, TripReport, SpeedingReport, AlertOverviewReport,
                    DeviceAlertReport, AlertDetailReport,PasswordResetRequestView, PasswordResetConfirmView)

router = DefaultRouter()
router.register(r'devices', DeviceViewSet, basename='device')  
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'geofences', GeoFenceViewSet, basename='geofence')
router.register(r'Users', UserViewSet, basename='User')
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'drivers', DriverViewSet, basename='driver')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'trips', TripViewSet, basename='trip')

urlpatterns = [

    # all lmodels vies , CRUD
    path('', include(router.urls)),

    # authntication 
    path('auth/user/register/', UserRegisterView.as_view(), name='user-register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),

    # verify email
    path('auth/verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify_email'),

    # reset password for user
    path('auth/reset-password/', PasswordResetRequestView.as_view(), name='reset-password-request'),
    path('auth/reset-password/<str:token>/', PasswordResetConfirmView.as_view(), name='reset-password-confirm'),

    # add new user:
    path('add-User/', AddNewUserView.as_view(), name='add-User'),

    # get feedback from USER:
    path('feedback/', FeedbackCreateView.as_view(), name='feedback_create'),
    
    # Reports:
    path('reports/motion-overview/', MotionOverviewReport.as_view(), name='motion_overview_report'),
    path('reports/mileage/', MileageReport.as_view(), name='mileage_report'),
    path('reports/daily-parking/', DailyParkingReport.as_view(), name='daily_parking_report'),
    path('reports/idling/', IdlingReport.as_view(), name='idling_report'),
    path('reports/ignition/', IgnitionReport.as_view(), name='ignition_report'),
    path('reports/offline/', OfflineReport.as_view(), name='offline_report'),
    path('reports/trip/', TripReport.as_view(), name='trip_report'),
    path('reports/speeding/', SpeedingReport.as_view(), name='speeding_report'),
    path('reports/alert-overview/', AlertOverviewReport.as_view(), name='alert_overview_report'),
    path('reports/device-alert/', DeviceAlertReport.as_view(), name='device_alert_report'),
    path('reports/alert-detail/<int:alert_id>/', AlertDetailReport.as_view(), name='alert_detail_report'),
    
]