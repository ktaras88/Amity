from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from ..models import User


class TestUserModel(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_superuser(self):
        user = User.objects.create_superuser(email='super@super.super', password='1234')
        self.assertIsInstance(user, User)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.email, 'super@super.super')

    def test_create_user(self):
        user = User.objects.create_user(email='user@user.user')
        self.assertIsInstance(user, User)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertEqual(user.email, 'user@user.user')

    def test_raise_error_when_no_email(self):
        self.assertRaises(ValueError, User.objects.create_user, email='')
        self.assertRaises(ValueError, User.objects.create_superuser, email='', password='1234')

    def test_raise_error_when_create_superuser_is_staff_is_false(self):
        self.assertRaises(ValueError, User.objects.create_superuser, email='s@s.s', password='1234', is_staff=False)

    def test_token_obtain_pair(self):
        url = '/api/v1.0/token/'
        user = User.objects.create_superuser(email='super@super.super', password='strong')

        response = self.client.post(url, {'email': 'super@super.super', 'password': 'strong'})
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' and 'refresh' in response.data)

        user.is_active = False
        user.save()
        response = self.client.post(url, {'email': 'super@super.super', 'password': 'strong'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_record_security_code(self):
    #     url = '/api/v1.0/users/security-code/'
    #     user = User.objects.create_user(email='user@use.user')
    #     user.send_security_code()
    #
    #     response = self.client.post()