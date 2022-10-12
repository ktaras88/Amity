from django.shortcuts import render

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView as SimpleJWTTokenObtainPairView

from .models import User
from .serializers import RequestEmailSerializer, SecurityCodeSerializer, TokenObtainPairSerializer


class TokenObtainPairView(SimpleJWTTokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


class ResetPasswordRequestEmail(generics.GenericAPIView):
    serializer_class = RequestEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            user.send_security_code()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'There is no account with that name.'}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordSecurityCode(generics.GenericAPIView):
    serializer_class = SecurityCodeSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data['security_code'] is not None and \
                serializer.validated_data['security_code'] == self.user.security_code:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Incorrect security code. Check your secure code or request for a new one.'},
                            status=status.HTTP_400_BAD_REQUEST)
