from django.urls import path, include
from .views import index

urlpatterns = [
    path('', index, name="index"),
    path('devices/', include('dashboard.devices.urls')),
    path('alerts/', include('dashboard.alerts.urls')),
    path('reports/', include('dashboard.reports.urls')),
    path('settings/', include('dashboard.settings.urls')),
]
