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
                                                  first_name='Fsuper', last_name='Lastsuper')
        self.client = APIClient()
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'super@super.super', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

        self.user1 = User.objects.create_user(email='user1@user1.user1', password='user1',
                                              first_name='User1_first', last_name='Last1')
        self.user2 = User.objects.create_user(email='user2@user2.user2', password='user2',
                                              first_name='User2_first', last_name='Last2')

        self.com1 = Community.objects.create(name='comm', state='AL', zip_code=1234, address='address1',
                                             contact_person=self.user, phone_number=1234567)
        self.com2 = Community.objects.create(name='commun', state='CT', zip_code=4321, address='address2',
                                             contact_person=self.user1, phone_number=7654321)
        self.com3 = Community.objects.create(name='community', state='DC', zip_code=1122, address='address3',
                                             contact_person=self.user2, phone_number=1122334)

    def test_retrieve_list_of_communities(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_search_by_name(self):
        response = self.client.get(self.url, data={'search': 'community'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], self.com3.name)

        response1 = self.client.get(self.url, data={'search': 'communi'})
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data['count'], 1)
        self.assertEqual(response1.data['results'][0]['name'], self.com3.name)

    def test_get_search_by_part_of_name(self):
        response = self.client.get(self.url, data={'search': 'comm'})
        self.assertEqual(response.data['results'][0], {'id': self.com1.id, 'name': self.com1.name, 'state': dict(US_STATES)[self.com1.state],
                                            'address': self.com1.address,
                                            'contact_person': str(self.com1.contact_person),
                                            'phone_number': str(self.com1.phone_number),
                                            'safety_status': self.com1.safety_status})
        self.assertEqual(response.data['results'][1], {'id': self.com2.id, 'name': self.com2.name, 'state': dict(US_STATES)[self.com2.state],
                                            'address': self.com2.address,
                                            'contact_person': str(self.com2.contact_person),
                                            'phone_number': str(self.com2.phone_number),
                                            'safety_status': self.com2.safety_status})
        self.assertEqual(response.data['results'][2], {'id': self.com3.id, 'name': self.com3.name, 'state': dict(US_STATES)[self.com3.state],
                                            'address': self.com3.address,
                                            'contact_person': str(self.com3.contact_person),
                                            'phone_number': str(self.com3.phone_number),
                                            'safety_status': self.com3.safety_status})

    def test_get_search_by_first_name(self):
        response = self.client.get(self.url, data={'search': 'user'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['contact_person'], str(self.com2.contact_person))
        self.assertEqual(response.data['results'][1]['contact_person'], str(self.com3.contact_person))

        response1 = self.client.get(self.url, data={'search': 'us'})
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data['count'], 2)
        self.assertEqual(response1.data['results'][0]['contact_person'], str(self.com2.contact_person))
        self.assertEqual(response1.data['results'][1]['contact_person'], str(self.com3.contact_person))

    def test_get_search_by_last_name(self):
        response = self.client.get(self.url, data={'search': 'lastsuper'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['contact_person'], str(self.com1.contact_person))

        response1 = self.client.get(self.url, data={'search': 'lasts'})
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data['count'], 1)
        self.assertEqual(response1.data['results'][0]['contact_person'], str(self.com1.contact_person))

    def test_get_search_by_state(self):
        response = self.client.get(self.url, data={'search': 'DC'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['state'], dict(US_STATES)[self.com3.state])

        response1 = self.client.get(self.url, data={'search': 'CT'})
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data['count'], 1)
        self.assertEqual(response1.data['results'][0]['state'], dict(US_STATES)[self.com2.state])

    def test_get_search_have_no_results(self):
        response = self.client.get(self.url, data={'search': 'qqqq'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])

        response1 = self.client.get(self.url, data={'search': 'qw'})
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data['results'], [])


class CommunitiesListAPIViewFilterTestCase(APITestCase):
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
        response = self.client.get(self.url + '?safety_status=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_communities_list_safety_status_with_filter_safety_off_show_only_safety_off_communities(self):
        response = self.client.get(self.url + '?safety_status=false')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_communities_list_custom_pagination_size_query_param_with_filter_safety_of_only(self):
        response = self.client.get(self.url + '?size=2&safety_status=false')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['count'], 3)
