from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from api.serializers import UserSerializer, AllUserSerializer
from core.models import User

class all(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_active=True)
    permission_classes = [permissions.AllowAny]
    serializer_class = AllUserSerializer

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def me(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=404)

    serializer = UserSerializer(request.user)
    return Response(serializer.data)

