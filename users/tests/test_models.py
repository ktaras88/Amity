from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from ..choices_types import ProfileRoles
User = get_user_model()


class TestUserModel(APITestCase):
    def test_create_superuser_create_profile_role(self):
        user = User.objects.create_superuser(email='super@super.super', password='1234')
        profile = user.profile_set.first()
        self.assertTrue(user.is_staff)
        self.assertEqual(user.email, 'super@super.super')
        self.assertTrue(profile)
        self.assertEqual(profile.role, ProfileRoles.AMITY_ADMINISTRATOR)

    def test_create_user_create_profile_role(self):
        user = User.objects.create_user(email='user@user.user')
        profile = user.profile_set.first()
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertEqual(user.email, 'user@user.user')
        self.assertTrue(profile)
        self.assertEqual(profile.role, ProfileRoles.RESIDENT)

    def test_raise_error_when_create_superuser_is_staff_is_false(self):
        self.assertRaises(ValueError, User.objects.create_superuser, email='s@s.s', password='1234', is_staff=False)

    def test_forgot_password_create_security_code(self):
        user = User.objects.create_user(email='user@user.user')
        user.security_code = user.generate_security_code()
        self.assertTrue(user.security_code)
