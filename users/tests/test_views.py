from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase, APIClient

from ..models import User, InvitationToken
from ..serializers import CreateNewPasswordSerializer


class TokenObtainPairViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/v1.0/token/'
        self.user = User.objects.create_superuser(email='super@super.super', password='strong')

    def test_ensure_that_client_provide_correct_data(self):
        response = self.client.post(self.url, {'email': 'super@super.super', 'password': 'strong'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)

    def test_ensure_that_client_provide_incorrect_data(self):
        response = self.client.post(self.url, {'email': 'uper@super.super', 'password': 'strong'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ensure_that_client_doesnt_provide_any_data(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ensure_that_inactive_user_have_no_access(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(self.url, {'email': 'super@super.super', 'password': 'strong'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ResetPasswordRequestEmailTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('v1.0:users:forgot-password')
        self.user = User.objects.create_user(email='user@user.user')

    def test_forgot_password_email_not_in_the_system(self):
        data = {'email': 'no@no.no'}
        response = self.client.post(self.url,  data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('error' in response.data)

    def test_forgot_password_email_in_the_system_check_response(self):
        data = {'email': self.user.email}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(User.objects.get(email=self.user.email).security_code), 6)

    def test_forgot_password_if_request_data_is_empty(self):
        data = {}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['email'][0]), 'This field is required.')


class NewSecurityCodeTestCase(APITestCase):
    def test_send_security_code_again_code_change(self):
        user = User.objects.create_user(email='user@user.user')
        security_code = user.generate_security_code()
        self.assertEqual(len(security_code), 6)
        self.assertFalse(user.security_code == security_code)


class ResetPasswordSecurityCodeTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('v1.0:users:security-code')
        self.user = User.objects.create_user(email='user@user.user', security_code='123456')

    def test_security_code_email_not_in_the_system(self):
        data = {'email': 'no@no.no', 'security_code': '000000'}
        response = self.client.post(self.url,  data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('error' in response.data)

    def test_security_code_wrong_code(self):
        data = {'email': self.user.email, 'security_code': '000000'}
        response = self.client.post(self.url,  data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('error' in response.data)

    def test_security_code_generate_token(self):
        data = {'email': self.user.email, 'security_code': self.user.security_code}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)

    def test_security_code_empty_data(self):
        data = {}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['email'][0]), 'This field is required.')


class CreateNewPasswordTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('v1.0:users:create-new-password')
        self.user = User.objects.create_user(email='user@user.user')
        self.token = str(InvitationToken.objects.filter(user=self.user).first())

    def test_create_new_password_wrong_token(self):
        data = {'token': 'wrong-token', 'password': 'User-password123', 'confirm_password': 'User-password123'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        with self.assertRaisesMessage(ValidationError, "There is no access to this page."):
            serializer = CreateNewPasswordSerializer(data=data)
            serializer.is_valid(raise_exception=True)

    def test_create_new_password_compare_passwords_not_the_same(self):
        data = {'token': self.token, 'password': 'User-password123', 'confirm_password': 'User-password321'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        with self.assertRaisesMessage(ValidationError, "Passwords do not match"):
            serializer = CreateNewPasswordSerializer(data=data)
            serializer.is_valid(raise_exception=True)

    def test_create_new_password_correct(self):
        data = {'token': self.token, 'password': 'User-password123', 'confirm_password': 'User-password123'}
        response = self.client.post(self.url, data, format='json')
        self.assertFalse(self.user.password == data['password'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_new_password_empty_data(self):
        data = {}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['token'][0]), 'This field is required.')

    def test_create_new_password_after_successful_request_token_was_removed_from_the_system(self):
        data = {'token': self.token, 'password': 'User-password123', 'confirm_password': 'User-password123'}
        response = self.client.post(self.url, data, format='json')
        self.assertFalse(InvitationToken.objects.filter(user=self.user).count())
        self.assertFalse(self.user.password == data['password'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
