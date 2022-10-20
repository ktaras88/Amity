import io
import tempfile

from PIL import Image
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import User


class TokenObtainPairViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('v1.0:token_obtain_pair')
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


class UserAvatarAPIViewTestCase(APITestCase):
    def generate_photo_file(self):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def setUp(self):
        self.user = User.objects.create_superuser(email='super@super.super', password='strong')
        self.url = reverse('v1.0:users:user-avatar', kwargs={'pk': self.user.id})
        self.user.avatar = self.generate_photo_file()
        self.user.avatar_coord = 100

        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        self.data = {'avatar': self.user.avatar, 'avatar_coord': self.user.avatar_coord}
        self.res = self.client.put(self.url, self.data)

    def test_get_data_for_authenticated_client(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(response.data['avatar'], self.user.avatar)
        self.assertEqual(response.data['avatar_coord'], self.user.avatar_coord)

    def test_get_data_for_un_authenticated_client(self):
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ensure_avatar_and_coord_recorded(self):
        # response = self.client.put(self.url, self.data)
        response = self.res
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(response.data['avatar'], self.user.avatar)
        self.assertEqual(response.data['avatar_coord'], self.user.avatar_coord)

    def test_delete_avatar_and_coord(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(bool(user.avatar), False)
        self.assertEqual(user.avatar_coord, None)
