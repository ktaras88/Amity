from rest_framework import generics, status
# from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import User
from .security_code import send_security_code
from .serializers import RequestEmailSerializer, SecurityCodeSerializer


class ResetPasswordRequestEmail(generics.GenericAPIView):
    # If user want to reset password, first we check his email and send security code
    serializer_class = RequestEmailSerializer
    # permission_classes = ()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        if User.objects.filter(email=email).exists():
            # if email is exist, send email and save code in user profile
            send_security_code(email, 'email_security_code.html')
            # redirect to security code page
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'There is no account with that name.'}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordSecurityCode(generics.GenericAPIView):
    serializer_class = SecurityCodeSerializer
    # permission_classes = ()

    def post(self, request):
        data = {
            'request': request,
            'data': request.data
        }
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        # check if this code and user code are the same
        # if yes: go to page change password, if not: rase exception
        if serializer.validated_data['security_code'] is not None and \
                serializer.validated_data['security_code'] == self.user.security_code:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Incorrect security code. Check your secure code or request for a new one.'},
                            status=status.HTTP_400_BAD_REQUEST)
