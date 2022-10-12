from django.urls import path

from users.views import ResetPasswordRequestEmail, ResetPasswordSecurityCode, ResetPasswordNewSecurityCode

urlpatterns = [
    path('forgot-password/', ResetPasswordRequestEmail.as_view(), name='reset-password'),
    path('security-code/', ResetPasswordSecurityCode.as_view(), name='security-code'),
    path('new-security-code/', ResetPasswordNewSecurityCode.as_view(), name='new-security-code'),
]
