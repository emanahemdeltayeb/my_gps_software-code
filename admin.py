from django.contrib import admin
from .models import Account, Role, User, Device, Alert, GeoFence,Trip,Driver, Feedback

# Register your models here.
admin.site.register(Account)
admin.site.register(Role)
admin.site.register(User)
admin.site.register(Device)
admin.site.register(Alert)
admin.site.register(GeoFence)
admin.site.register(Trip)
admin.site.register(Driver)
admin.site.register(Feedback)