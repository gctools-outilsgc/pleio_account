from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework import generics, viewsets, permissions
from api.serializers import UserSerializer, RegisterSerializer, LoginSerializer, LoginTestSerializer, AllUserSerializer
from api.permissions import IsAdminPermission
from core.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status

from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

class all_users(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AllUserSerializer

# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.create(user=user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token.key
        })

# Login API
class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def get_serializer_context(self):
        context = super(LoginAPI, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token.key
        })

# Logout API
class LogoutAPI(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    def post(self, request):
        logout(request)
        return Response()

# Get User API
class UserAPI(generics.RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class Login(APIView):

    permission_classes = (permissions.AllowAny,)
    authentication_classes = (SessionAuthentication,)

    def get_serializer_context(self):
        context = super(Login, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def post(self, request):
        serializer = LoginTestSerializer(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response({
            "user": UserSerializer(user).data
        })