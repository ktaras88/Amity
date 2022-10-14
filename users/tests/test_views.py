from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from ..models import User


class TokenObtainPairViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/v1.0/token/'

    def test_ensure_that_client_provide_correct_data(self):
        User.objects.create_superuser(email='super@super.super', password='strong')
        response = self.client.post(self.url, {'email': 'super@super.super', 'password': 'strong'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)

    def test_ensure_that_client_provide_incorrect_data(self):
        User.objects.create_superuser(email='super@super.super', password='strong')
        response = self.client.post(self.url, {'email': 'uper@super.super', 'password': 'strong'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ensure_that_inactive_user_have_no_access(self):
        user = User.objects.create_superuser(email='super@super.super', password='strong')
        user.is_active = False
        user.save()
        response = self.client.post(self.url, {'email': 'super@super.super', 'password': 'strong'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
