from django.contrib.auth.backends import BaseBackend
from .models import User

# Custom authentication backend This backend directly compares plain-text passwords
class UserBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Fetch the user by username
            user = User.objects.get(username=username)

            # Compare plain-text passwords
            if user.password == password:  # Directly compare plain-text passwords
                return user
        except User.DoesNotExist:
            return None  # User not found

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None  # User not found