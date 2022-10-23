from django.urls import reverse
from django.contrib.auth import get_user_model
from localflavor.us.us_states import US_STATES

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from communities.models import Community

User = get_user_model()


class CommunitiesListAPIViewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('v1.0:communities:communities-list')
        self.user = User.objects.create_superuser(email='super@super.super', password='strong',
                                                  first_name='First-super', last_name='Last-super')
        self.client = APIClient()
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'super@super.super', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

        self.com1 = Community.objects.create(name='Bbb', state='CO', zip_code=1111, address='address1',
                                             phone_number=1111111, safety_status=True)
        self.com2 = Community.objects.create(name='Aaaa', state='AL', zip_code=1111, address='address2',
                                             phone_number=1111111, safety_status=True)
        self.com3 = Community.objects.create(name='Www', state='CT', zip_code=1111, address='address3',
                                             phone_number=1111111, safety_status=False)
        self.com4 = Community.objects.create(name='Www', state='DC', zip_code=1111, address='address4',
                                             phone_number=1111111, safety_status=False)
        self.com5 = Community.objects.create(name='Aaa', state='DE', zip_code=1111, address='address5',
                                             phone_number=1111111, safety_status=False)

    def test_communities_list_safety_status_without_filter_show_all_communities(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_communities_list_custom_pagination_size_query_param(self):
        response = self.client.get(self.url + '?size=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_communities_list_safety_status_with_filter_safety_on_show_only_safety_on_communities(self):
        response = self.client.get(self.url + '?safety_on=True')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_communities_list_safety_status_with_filter_safety_off_show_only_safety_off_communities(self):
        response = self.client.get(self.url + '?safety_off=True')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_communities_list_safety_status_with_filter_safety_off_and_safety_on_show_all_communities(self):
        response = self.client.get(self.url + '?safety_on=True&safety_off=True')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_communities_list_custom_pagination_size_query_param_with_filter_safety_of_only(self):
        response = self.client.get(self.url + '?size=2&safety_off=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['count'], 3)
