from django.urls import path

from users.views import ResetPasswordRequestEmail, ResetPasswordSecurityCode, CreateNewPassword, UserAvatarAPIView, \
    UserGeneralInformationView, UserContactInformationView, UserPasswordInformationView

app_name = 'users'

urlpatterns = [
    path('forgot-password/', ResetPasswordRequestEmail.as_view(), name='forgot-password'),
    path('security-code/', ResetPasswordSecurityCode.as_view(), name='security-code'),
    path('new-security-code/', ResetPasswordRequestEmail.as_view(), name='new-security-code'),
    path('create-new-password/', CreateNewPassword.as_view(), name='create-new-password'),
    path('<int:pk>/avatar/', UserAvatarAPIView.as_view(), name='user-avatar'),
    path('<int:pk>/general-info/', UserGeneralInformationView.as_view(), name='user-general-info'),
    path('<int:pk>/contact-info/', UserContactInformationView.as_view(), name='user-contact-info'),
    path('<int:pk>/password-info/', UserPasswordInformationView.as_view(), name='user-password-info'),
]
