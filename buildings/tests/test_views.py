from django.urls import reverse
from django.contrib.auth import get_user_model
from localflavor.us.us_states import US_STATES

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from buildings.models import Building
from communities.models import Community

User = get_user_model()


class BuildingViewSetTestCase(APITestCase):
    def setUp(self):

        self.user = User.objects.create_superuser(email='super@super.super', password='strong',
                                                  first_name='Fsuper', last_name='Lastsuper')
        self.client = APIClient()
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'super@super.super', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

        self.community1 = Community.objects.create(name='community1', state='AL', zip_code=1234, address='address1',
                                                   contact_person=self.user, phone_number=1234567)
        self.url = reverse('v1.0:buildings:buildings-list', args=[self.community1.id])
        self.build1 = Building.objects.create(community_id=self.community1.id, name='building1', state='AL',
                                              address='address1', contact_person=self.user, phone_number=1234567)
        self.build2 = Building.objects.create(community_id=self.community1.id, name='building2', state='AR',
                                              address='address2', contact_person=self.user, phone_number=7654321)

    def test_retrieve_list_of_buildings(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['name'], self.build1.name)
        self.assertEqual(response.data['results'][1]['name'], self.build2.name)

    def test_correct_building_creation(self):
        data = {
            "name": "building_20",
            "state": "AL",
            "address": "addressb20",
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['state'], data['state'])
        self.assertEqual(response.data['address'], data['address'])
        self.assertEqual(response.data['safety_status'], True)

    def test_wrong_community_id(self):
        data = {
            "name": "building_20",
            "state": "AL",
            "address": "addressb20",
        }
        url = reverse('v1.0:buildings:buildings-list', args=[333])
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['error'][0]), 'There is no such community')

    def test_creating_without_name_of_building(self):
        data = {
            "name": "",
            "state": "AL",
            "address": "addressb20",
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['name'][0]), 'This field may not be blank.')

    def test_creating_without_address_of_building(self):
        data = {
            "name": "building_20",
            "state": "AL",
            "address": "",
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['address'][0]), 'This field may not be blank.')
