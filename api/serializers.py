from rest_framework import serializers
from core.models import User
from django.contrib import auth
from django.contrib.auth import authenticate
from axes.attempts import is_already_locked
from axes.utils import get_credentials, get_lockout_message
from axes.models import AccessAttempt
from core.models import User
from emailvalidator.validator import is_email_valid

class AllUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email']

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'username', 'email')

 # Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        email = value.lower()

        if not is_email_valid(email):
            raise serializers.ValidationError("Invalid email address.")

        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email

        raise serializers.ValidationError("Account with email already exists.")

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['email'].lower(), validated_data['name'], validated_data['password'])

        user.send_activation_token(self.context['request'])

        return user

 # Login Serializer
class LoginSerializer(serializers.Serializer):
        
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(self.context['request'], **data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")

class LoginTestSerializer(serializers.Serializer):
    username = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):

        credentials = {
            'username': attrs['username'],
            'password': attrs['password'],
            'auth-username': attrs['username'],
            'auth-password': attrs['password'],
        }

        user = authenticate(self.context['request'], **credentials)

        if not user:
            attempts = AccessAttempt.objects.filter(username=attrs['username'])
            # TODO: Build out lock out error reporting

            raise serializers.ValidationError(attempts[0].failures_since_start)
            # raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError('User is disabled.')

        creds = get_credentials(**credentials)

        if is_already_locked(self.context['request'], creds):
            error_msg = get_lockout_message()
            raise serializers.ValidationError(error_msg)

        return {'user': user}

 # Activate User Serializer
class ActivateUserSerializer(serializers.Serializer):
    activation_token = serializers.CharField()

    def validate(self, data):
        user = User.activate_user(None, data['activation_token'])

        if user:
            return {'user': user}

        raise serializers.ValidationError("Invalid token")