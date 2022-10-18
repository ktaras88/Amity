from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.auth.password_validation import (MinimumLengthValidator)
from users.validators import (MaximumLengthValidator, NumberValidator, UppercaseValidator,
                              LowercaseValidator, SymbolValidator)
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from ..models import User, InvitationToken


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
        # Minimum length validation
        expected_error_min = "This password is too short. It must contain at least %d characters."
        self.assertIsNone(MinimumLengthValidator().validate('12345678'))
        self.assertIsNone(MinimumLengthValidator(min_length=8).validate('12345678'))

        with self.assertRaises(ValidationError) as ex:
            MinimumLengthValidator().validate('1234567')
        self.assertEqual(ex.exception.messages, [expected_error_min % 8])
        self.assertEqual(ex.exception.error_list[0].code, 'password_too_short')

        with self.assertRaises(ValidationError) as cm:
            MinimumLengthValidator(min_length=8).validate('12345')
        self.assertEqual(cm.exception.messages, [expected_error_min % 8])

        # Maximum length validation
        expected_error_max = "This password must contain at most %(max_length)d characters."
        self.assertIsNone(MaximumLengthValidator().validate('tjdi32ndki12'))
        self.assertIsNone(MaximumLengthValidator(max_length=128).validate('tjdi32ndki12'))

        # validate password with 129 symbols
        with self.assertRaises(ValidationError) as ex:
            MaximumLengthValidator().validate('rvsdbhrthnngfnewrvsdcge1346tfsedfvtjFhmhgwsgsnrsegbgfnryyzetahdnzfmtusjehfnfjysruaengdngkdjahthfxthysykysjtdfbfdbfgtjhtrsjsrysmy6')
        self.assertEqual(ex.exception.messages, [expected_error_max % 128])
        self.assertEqual(ex.exception.error_list[0].code, 'password_too_long')

        with self.assertRaises(ValidationError) as cm:
            MaximumLengthValidator(max_length=128).validate('rvsdbhrthnngfnewrvsdcge1346tfsedfvtjFhmhgwsgsnrsegbgfnryyzetahdnzfmtusjehfnfjysruaengdngkdjahthfxthysykysjtdfbfdbfgtjhtrsjsrysmy6')
        self.assertEqual(cm.exception.messages, [expected_error_max % 128])

        # Uppercase validation
        expected_error_up = "The password must contain at least 1 uppercase letter, A-Z."
        self.assertIsNone(UppercaseValidator().validate('573Jhducni'))

        with self.assertRaises(ValidationError) as ex:
            UppercaseValidator().validate('12345678')
        self.assertEqual(ex.exception.messages, [expected_error_up])
        self.assertEqual(ex.exception.error_list[0].code, 'password_no_upper')

        # Lowercase validation
        expected_error_lo = "The password must contain at least 1 lowercase letter, a-z."
        self.assertIsNone(LowercaseValidator().validate('84cucelJdr'))

        with self.assertRaises(ValidationError) as ex:
            LowercaseValidator().validate('12345678')
        self.assertEqual(ex.exception.messages, [expected_error_lo])
        self.assertEqual(ex.exception.error_list[0].code, 'password_no_lower')

        # Symbol validation
        expected_error_sym = "The password must contain at least 1 symbol: ()[]{}|`~!@#$%^&*_-+=;:'\",<>./?"
        self.assertIsNone(UppercaseValidator().validate('84cuc$*elJdr'))

        with self.assertRaises(ValidationError) as ex:
            UppercaseValidator().validate('12345678')
        self.assertEqual(ex.exception.messages, [expected_error_sym])
        self.assertEqual(ex.exception.error_list[0].code, 'password_no_symbol')

        # Number validation
        expected_error_num = "The password must contain at least %(min_digits)d digit(s), 0-9."
        self.assertIsNone(NumberValidator().validate('84cuc$*elJdr'))

        with self.assertRaises(ValidationError) as ex:
            NumberValidator().validate('advmkdJmd$')
        self.assertEqual(ex.exception.messages, [expected_error_num])
        self.assertEqual(ex.exception.error_list[0].code, 'password_no_number')

        with self.assertRaises(ValidationError) as cm:
            NumberValidator(min_digits=5).validate('12g34ndjcnI')
        self.assertEqual(cm.exception.messages, [expected_error_num % 4])
