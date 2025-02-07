from rest_framework import permissions

class IsAccountOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an account to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the logged-in user is the owner of the account
        return obj == request.user

class IsUserOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an end user to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the logged-in user is the owner of the end user
        return obj.owner == request.user

class IsDeviceOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a device to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the logged-in user is the owner of the device
        return obj.user.owner == request.user

class IsAlertOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an alert to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the logged-in user is the owner of the alert's device
        return obj.device.user.owner == request.user

class IsGeoFenceOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a geofence to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the logged-in user is the owner of the geofence's device
        return obj.device.user.owner == request.user

class IsOwnerOrDevice(permissions.BasePermission):
    """
    Custom permission to only allow owners of the device or the device itself to access the trip.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the user is the owner of the device
        if obj.device.user.owner == request.user:
            return True
        # Check if the request is coming from the device itself
        # Assuming the device sends a token or some identifier in the request headers
        device_token = request.headers.get('Device-Token')
        if device_token and device_token == obj.device.websocket_channel_name:
            return True
        return False

class IsDriverOwner(permissions.BasePermission):
    """
    Permission to allow only the driver owner or their staff to access the driver.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the driver belongs to the logged-in user or their parent account
        return obj.user == request.user or request.user in obj.user.parent.users.all()
