from django.urls import path

from users.views import ResetPasswordRequestEmail, ResetPasswordSecurityCode, CreateNewPassword

urlpatterns = [
    path('forgot-password/', ResetPasswordRequestEmail.as_view(), name='reset-password'),
    path('security-code/', ResetPasswordSecurityCode.as_view(), name='security-code'),
    path('new-security-code/', ResetPasswordRequestEmail.as_view(), name='new-security-code'),
    path('create-new-password/', CreateNewPassword.as_view(), name='create-new-password'),
]