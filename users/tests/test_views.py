from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.auth.password_validation import (MinimumLengthValidator)
from users.validators import (MaximumLengthValidator, NumberValidator, UppercaseValidator,
                              LowercaseValidator, SymbolValidator)
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.models import InvitationToken
User = get_user_model()


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


class CreateNewPasswordTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('v1.0:users:create-new-password')
        self.user = User.objects.create_user(email='user@user.user')
        self.token = str(InvitationToken.objects.filter(user=self.user).first())

    def test_create_new_password_wrong_token(self):
        data = {'token': self.token, 'password': 'User-password123', 'confirm_password': 'User-password123'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_new_password_compare_passwords_not_the_same(self):
        data = {'token': self.token, 'password': 'User-password123', 'confirm_password': 'User-password321'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ensure_password_is_valid(self):
        data = {'token': self.token, 'password': '12Jsirvm&*knv4', 'confirm_password': '12Jsirvm&*knv4'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ensure_minimum_length_is_invalid(self):
        data = {'token': self.token, 'password': '12Jsir*', 'confirm_password': '12Jsir*'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], "This password is too short. It must contain at least %d characters." % 8)

    def test_ensure_maximum_length_is_invalid(self):
        data = {'token': self.token, 'password': '12Jsir*rvsdbhrthnngfnewrvsdcge1346tfsedfvtjFhmhgwsgsnrsegbgfnryyzetahdnzfmtusjehfnfjysruaengdngkdjahthfxthysykysjtdfbfdbfgtjhtrsjsrysmy6',
                'confirm_password': '12Jsir*rvsdbhrthnngfnewrvsdcge1346tfsedfvtjFhmhgwsgsnrsegbgfnryyzetahdnzfmtusjehfnfjysruaengdngkdjahthfxthysykysjtdfbfdbfgtjhtrsjsrysmy6'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], "This password must contain at most %d characters." % 128)

    def test_ensure_password_include_no_uppercase_letters(self):
        data = {'token': self.token, 'password': 'disnt&ie)1',
                'confirm_password': 'disnt&ie)1'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], "The password must contain at least 1 uppercase letter, A-Z.")

    def test_ensure_password_include_no_lowercase_letters(self):
        data = {'token': self.token, 'password': '174HDOR9SH&%JD',
                'confirm_password': '174HDOR9SH&%JD'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], "The password must contain at least 1 lowercase letter, a-z.")

    def test_ensure_password_include_no_symbols(self):
        data = {'token': self.token, 'password': 'irnxyYNDR5375',
                'confirm_password': 'irnxyYNDR5375'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], "The password must contain at least 1 special character: " +
                "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?")

    def test_ensure_password_include_no_digits(self):
        data = {'token': self.token, 'password': 'Yjduc&%jeu', 'confirm_password': 'Yjduc&%jeu'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], "The password must contain at least 1 digit, 0-9.")
