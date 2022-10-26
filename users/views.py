from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView as SimpleJWTTokenObtainPairView

from amity_api.permission import IsOwnerNotForResident
from .models import InvitationToken
from .serializers import RequestEmailSerializer, SecurityCodeSerializer, TokenObtainPairSerializer, \
    CreateNewPasswordSerializer, UserAvatarSerializer, UserGeneralInformationSerializer, \
    UserContactInformationSerializer, UserPasswordInformationSerializer

User = get_user_model()


class TokenObtainPairView(SimpleJWTTokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


class ResetPasswordRequestEmail(generics.GenericAPIView):
    serializer_class = RequestEmailSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        if user := User.objects.filter(email=email).first():
            user.send_security_code()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'There is no account with that email.'}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordSecurityCode(generics.GenericAPIView):
    serializer_class = SecurityCodeSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if user := User.objects.filter(email=serializer.validated_data['email']).first():
            if serializer.validated_data['security_code'] == user.security_code:
                token, _ = InvitationToken.objects.get_or_create(user=user)
                return Response({'token': str(token)}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Incorrect security code. Check your secure code or request for a new one.'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'There is no user with that email.'}, status=status.HTTP_400_BAD_REQUEST)


class CreateNewPassword(generics.GenericAPIView):
    serializer_class = CreateNewPasswordSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user.set_password(serializer.validated_data['password'])
        user.save()

        InvitationToken.objects.filter(user_id=user.id).delete()

        return Response(status=status.HTTP_200_OK)


class UserAvatarAPIView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserAvatarSerializer
    permission_classes = (IsOwnerNotForResident, )

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.avatar:
            if instance.avatar_coord:
                instance.avatar.delete()
                instance.avatar_coord = None
                instance.save()
                return Response({'message': 'Avatar removed'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'error': 'There is no avatar_coord.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'There is no avatar.'}, status=status.HTTP_400_BAD_REQUEST)


class UserGeneralInformationView(generics.RetrieveUpdateAPIView):
    serializer_class = UserGeneralInformationSerializer
    queryset = User.objects.all()
    permission_classes = (IsOwnerNotForResident,)


class UserContactInformationView(generics.RetrieveUpdateAPIView):
    serializer_class = UserContactInformationSerializer
    queryset = User.objects.all()
    permission_classes = (IsOwnerNotForResident,)


class UserPasswordInformationView(generics.RetrieveUpdateAPIView):
    serializer_class = UserPasswordInformationSerializer
    queryset = User.objects.all()
    permission_classes = (IsOwnerNotForResident,)
