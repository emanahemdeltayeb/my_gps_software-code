"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar
from django.contrib import admin
from django.urls import path, include  # include is used to include app-level URLs
from django_prometheus import exports
from django.shortcuts import render

def authorize(request):
    return render(request, 'auth/authorize.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),
    path('metrics/', exports.ExportToDjangoView),

    path('', include(('dashboard.urls', 'dashboard'), namespace="dashboard")),
    path('api/', include('api.urls')),  # Pointing to the app-specific URLs
    path('authorize', authorize)
]
