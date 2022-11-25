from django.urls import path

from users.views import ResetPasswordRequestEmail, ResetPasswordSecurityCode, CreateNewPassword, UserAvatarAPIView, \
    UserProfileInformationAPIView, UserPasswordInformationView, UsersRoleListAPIView, \
    GetAuthenticatedUserIdAPIView, NewMemberAPIView, PropertiesWithoutContactPersonAPIView, \
    ActivateSpecificMemberAPIView, BelowRolesListAPIView

app_name = 'users'

urlpatterns = [
    path('', NewMemberAPIView.as_view(), name='create-new-member'),
    path('<int:pk>/activate/', ActivateSpecificMemberAPIView.as_view(), name='activate-member'),
    path('forgot-password/', ResetPasswordRequestEmail.as_view(), name='forgot-password'),
    path('security-code/', ResetPasswordSecurityCode.as_view(), name='security-code'),
    path('get-authenticated-user-id/', GetAuthenticatedUserIdAPIView.as_view(), name='get-authenticated-user-id'),
    path('new-security-code/', ResetPasswordRequestEmail.as_view(), name='new-security-code'),
    path('create-new-password/', CreateNewPassword.as_view(), name='create-new-password'),
    path('<int:pk>/avatar/', UserAvatarAPIView.as_view(), name='user-avatar'),
    path('<int:pk>/profile-info/', UserProfileInformationAPIView.as_view(), name='profile-info'),
    path('<int:pk>/password-info/', UserPasswordInformationView.as_view(), name='user-password-info'),
    path('roles/', BelowRolesListAPIView.as_view(), name='roles-list'),
    path('role-list/<str:role>/', UsersRoleListAPIView.as_view(), name='users-role-list'),
    path('property-list/<str:role>/', PropertiesWithoutContactPersonAPIView.as_view(), name='property-list'),
]
