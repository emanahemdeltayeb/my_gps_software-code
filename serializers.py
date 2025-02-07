from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from .models import Account, Role, User, Device, Alert, GeoFence, Trip, Driver, Feedback
from django.core.exceptions import ValidationError

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'
        read_only_fields = ['user']  # Prevent user from being set via API

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = '__all__'

class GeoFenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeoFence
        fields = '__all__'

class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = '__all__'

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = '__all__'
#         extra_kwargs = {'password': {'write_only': True}}
#         read_only_fields = ['owner']

#     def create(self, validated_data):
#         password = validated_data.pop('password')
#         user = User(**validated_data)
#         user.set_password(password)  # Hash the password
#         user.save()
#         return user
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'status']  # Include required fields
        extra_kwargs = {
            'password': {'write_only': True},
            'parent': {'read_only': True},  # Prevent manual assignment of parent account
        }

    def create(self, validated_data):
        # Extract password and hash it
        password = validated_data.pop('password')
        validated_data['password'] = make_password(password)

        # Create the user
        user = User.objects.create(**validated_data)

        # Create an account for the user and link it
        account = Account.objects.create(
            owner=user,
            name=f"{user.username}'s Workspace",  # Customize the account name
            credits=100  # Initial credits
        )

        # Link the user to the account via `parent` field
        user.parent = account
        user.save()

        return user
    
class AccountRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Account
        fields ='__all__'

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data, password=password)
        return user
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        return user
    
class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}  # Hide password in responses

    def create(self, validated_data):
        password = validated_data.pop('password')
        account = Account(**validated_data)
        account.set_password(password)  # Hash the password
        account.save()
        return account

class AddUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}} # Hide password in responses


    def create(self, validated_data):
        # Get the Account owner from the context
        account_owner = self.context['request'].user.owner

        # Create the new User
        end_user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=make_password(validated_data['password']),  # Hash the password
            owner=account_owner,  # Set the owner to the Account of the logged-in User
        )
        return end_user

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # Check if the email exists in the User model
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_token(self, value):
        # Check if the token is valid for either Account or User
        account = Account.objects.filter(reset_password_token=value).first()
        user = User.objects.filter(reset_password_token=value).first()
        if not account and not user:
            raise serializers.ValidationError("Invalid or expired token.")
        return value

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = '__all__'
        read_only_fields = ['created_at']  # Prevent modification of created_at field

    def validate_license_number(self, value):
        """
        Ensure that the license number is unique.
        """
        if Driver.objects.filter(license_number=value).exists():
            raise ValidationError("License number must be unique.")
        return value

    def create(self, validated_data):
        """
        Create a new driver and associate them with the authenticated user.
        """
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            raise ValidationError("Authentication required to create a driver.")

        # Automatically assign the authenticated user
        validated_data['user'] = request.user

        # Create and return the driver
        return Driver.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update an existing driver's data.
        """
        # Ensure that the user is not being changed
        validated_data.pop('user', None)

        # Update and save the instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

    def validate(self, data):
        
        return data