from rest_framework import serializers
from core.models import User

class UserSerializer(serializers.ModelSerializer):
    guid = serializers.IntegerField(source='id')
    isAdmin = serializers.BooleanField(source='is_admin')

    class Meta:
        model = User
        fields = ('guid', 'username', 'name', 'email', 'isAdmin')

class AllUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email']