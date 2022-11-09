from django.urls import reverse
from django.contrib.auth import get_user_model
from localflavor.us.us_states import US_STATES

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from buildings.models import Building
from communities.models import Community
from users.choices_types import ProfileRoles
from users.models import Profile

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
        response = self.client.get(self.url, data={'search': 'com'})
        self.assertEqual(dict(response.data['results'][0]), {'id': self.com1.id, 'name': self.com1.name,
                                                             'state': dict(US_STATES)[self.com1.state],
                                                             'address': self.com1.address,
                                                             'contact_person_name': self.com1.contact_person.get_full_name(),
                                                             'phone_number': str(self.com1.phone_number),
                                                             'safety_status': self.com1.safety_status})
        self.assertEqual(dict(response.data['results'][1]), {'id': self.com2.id, 'name': self.com2.name,
                                                             'state': dict(US_STATES)[self.com2.state],
                                                             'address': self.com2.address,
                                                             'contact_person_name': self.com2.contact_person.get_full_name(),
                                                             'phone_number': str(self.com2.phone_number),
                                                             'safety_status': self.com2.safety_status})
        self.assertEqual(dict(response.data['results'][2]), {'id': self.com3.id, 'name': self.com3.name,
                                                             'state': dict(US_STATES)[self.com3.state],
                                                             'address': self.com3.address,
                                                             'contact_person_name': self.com3.contact_person.get_full_name(),
                                                             'phone_number': str(self.com3.phone_number),
                                                             'safety_status': self.com3.safety_status})

    def test_get_search_by_contact_person(self):
        response = self.client.get(self.url, data={'search': 'lastsuper'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['contact_person_name'], str(self.com1.contact_person))

        response1 = self.client.get(self.url, data={'search': 'lasts'})
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data['count'], 1)
        self.assertEqual(response1.data['results'][0]['contact_person_name'], str(self.com1.contact_person))

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
        self.user1 = User.objects.create_user(email='user1@user1.user1', password='user1',
                                              first_name='User1_first', last_name='Last1')
        self.user2 = User.objects.create_user(email='user2@user2.user2', password='user2',
                                              first_name='User2_first', last_name='Last2')
        self.user3 = User.objects.create_user(email='user3@user3.user3', password='user3',
                                              first_name='User3_first', last_name='Last3')
        self.user4 = User.objects.create_user(email='user4@user4.user4', password='user4',
                                              first_name='User4_first', last_name='Last4')
        self.client = APIClient()
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'super@super.super', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

        self.com1 = Community.objects.create(name='Bbb', state='CO', zip_code=1111, address='address1',
                                             contact_person=self.user4, phone_number=1111111, safety_status=True)
        self.com2 = Community.objects.create(name='Aaaa', state='AL', zip_code=1111, address='address2',
                                             contact_person=self.user, phone_number=1111111, safety_status=True)
        self.com3 = Community.objects.create(name='Www', state='CT', zip_code=1111, address='address3',
                                             contact_person=self.user1, phone_number=1111111, safety_status=False)
        self.com4 = Community.objects.create(name='Www', state='DC', zip_code=1111, address='address4',
                                             contact_person=self.user3, phone_number=1111111, safety_status=False)
        self.com5 = Community.objects.create(name='Aaa', state='DE', zip_code=1111, address='address5',
                                             contact_person=self.user2, phone_number=1111111, safety_status=False)

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

    def test_communities_list_ascending_sort_by_name(self):
        response = self.client.get(self.url + '?ordering=name')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_order = [item['name'] for item in response.data['results']]
        expected_order = [self.com5.__dict__['name'], self.com2.__dict__['name'], self.com1.__dict__['name'],
                          self.com3.__dict__['name'], self.com4.__dict__['name']]
        self.assertEqual(response_order, expected_order)

    def test_communities_list_descending_sort_by_name(self):
        response = self.client.get(self.url + '?ordering=-name')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_order = [item['name'] for item in response.data['results']]
        expected_order = [self.com4.__dict__['name'], self.com3.__dict__['name'], self.com1.__dict__['name'],
                          self.com2.__dict__['name'], self.com5.__dict__['name']]
        self.assertEqual(response_order, expected_order)

    def test_communities_list_ascending_sort_by_name_and_address(self):
        response = self.client.get(self.url + '?ordering=name,address')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_order = [{item['name']: item['address']} for item in response.data['results']]
        expected_order = [{self.com5.__dict__['name']: self.com5.__dict__['address']},
                          {self.com2.__dict__['name']: self.com2.__dict__['address']},
                          {self.com1.__dict__['name']: self.com1.__dict__['address']},
                          {self.com3.__dict__['name']: self.com3.__dict__['address']},
                          {self.com4.__dict__['name']: self.com4.__dict__['address']}]
        self.assertEqual(response_order, expected_order)

    def test_communities_list_descending_sort_by_name_and_address(self):
        response = self.client.get(self.url + '?ordering=-name,-address')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_order = [{item['name']: item['address']} for item in response.data['results']]
        expected_order = [{self.com4.__dict__['name']: self.com4.__dict__['address']},
                          {self.com3.__dict__['name']: self.com3.__dict__['address']},
                          {self.com1.__dict__['name']: self.com1.__dict__['address']},
                          {self.com2.__dict__['name']: self.com2.__dict__['address']},
                          {self.com5.__dict__['name']: self.com5.__dict__['address']}]
        self.assertEqual(response_order, expected_order)

    def test_communities_list_ascending_sort_by_state(self):
        response = self.client.get(self.url + '?ordering=state')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_order = [item['state'] for item in response.data['results']]
        expected_order = [dict(US_STATES)[self.com2.state], dict(US_STATES)[self.com1.state],
                          dict(US_STATES)[self.com3.state], dict(US_STATES)[self.com4.state],
                          dict(US_STATES)[self.com5.state]]
        self.assertEqual(response_order, expected_order)

    def test_communities_list_descending_sort_by_state(self):
        response = self.client.get(self.url + '?ordering=-state')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_order = [item['state'] for item in response.data['results']]
        expected_order = [dict(US_STATES)[self.com5.state], dict(US_STATES)[self.com4.state],
                          dict(US_STATES)[self.com3.state], dict(US_STATES)[self.com1.state],
                          dict(US_STATES)[self.com2.state]]
        self.assertEqual(response_order, expected_order)

    def test_communities_list_ascending_sort_by_contact_person(self):
        response = self.client.get(self.url + '?ordering=contact_person_name')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_order = [item['contact_person_name'] for item in response.data['results']]
        expected_order = [str(self.user), str(self.user1), str(self.user2), str(self.user3), str(self.user4)]
        self.assertEqual(response_order, expected_order)

    def test_communities_list_descending_sort_by_contact_person(self):
        response = self.client.get(self.url + '?ordering=-contact_person_name')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_order = [item['contact_person_name'] for item in response.data['results']]
        expected_order = [str(self.user4), str(self.user3), str(self.user2), str(self.user1), str(self.user)]
        self.assertEqual(response_order, expected_order)


class CommunitiesListAPIViewSwitchSafetyStatusTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(email='super@super.super', password='strong',
                                                  first_name='First-super', last_name='Last-super')
        self.com = Community.objects.create(name='Davida', state='DC', zip_code=1111, address='davida_address',
                                            contact_person=self.user, phone_number=1230456204, safety_status=True)
        self.url = reverse('v1.0:communities:switch-safety-status', args=[self.com.id])
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'super@super.super', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_ensure_switch_safety_status_for_community_works_correctly(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['safety_status'], False)

    def test_ensure_switch_safety_status_for_community_by_non_authorised_not_work(self):
        self.client.force_authenticate(user=None, token=None)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_ensure_switch_safety_status_for_community_by_not_admin_or_supervisor_not_work(self):
        self.user1 = User.objects.create_user(email='user1@user1.user1', password='user1',
                                              first_name='User1_first', last_name='Last1')
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user1@user1.user1', 'password': 'user1'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')


class CommunityDetailedPageTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(email='super@super.super', password='strong',
                                                  first_name='First-super', last_name='Last-super')
        self.com = Community.objects.create(name='Davida', state='DC', zip_code=1111, address='davida_address',
                                            contact_person=self.user, phone_number=1230456204, safety_status=True)
        self.build1 = Building.objects.create(community_id=self.com.id, name='building1', state='DC',
                                              address='address1', contact_person=self.user, phone_number=1234567)
        self.build2 = Building.objects.create(community_id=self.com.id, name='building2', state='DC',
                                              address='address2', contact_person=self.user, phone_number=7654321)
        self.url = reverse('v1.0:communities:switch-safety-status', args=[self.com.id])
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'super@super.super', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_ensure_that_safety_status_switching_for_communities_and_related_buildings(self):
        self.assertEqual(self.com.safety_status, True)
        self.assertEqual(self.build1.safety_status, True)
        self.assertEqual(self.build2.safety_status, True)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['safety_status'], False)
        self.assertEqual(Building.objects.get(id=self.build1.id).safety_status, False)
        self.assertEqual(Building.objects.get(id=self.build2.id).safety_status, False)

    def test_communities_detailed_page_ensure_switch_safety_status_by_non_authorised_not_work(self):
        self.client.force_authenticate(user=None, token=None)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_communities_detailed_page_ensure_switch_safety_status_by_not_admin_or_supervisor_not_work(self):
        self.user = User.objects.create_user(email='user@user.user', password='user',
                                             first_name='User_first', last_name='Last')
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user@user.user', 'password': 'user'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')


class CommunityAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(email='super@super.super', password='strong',
                                                  first_name='First-super', last_name='Last-super')
        self.user1 = User.objects.create_user(email='user1@user1.user1', password='user1',
                                              first_name='User1_first', last_name='Last1', role=ProfileRoles.SUPERVISOR)
        self.user2 = User.objects.create_user(email='user2@user2.user2', password='user2',
                                              first_name='User2_first', last_name='Last2', role=ProfileRoles.SUPERVISOR)
        self.com = Community.objects.create(name='Community name', state='DC', zip_code=1111,
                                            address='Community address',
                                            contact_person=self.user1, phone_number=1230456204, safety_status=True)
        self.url = reverse('v1.0:communities:communities-detail', args=[self.com.id])

    def test_permission_class_IsAmityAdministratorOrCommunityContactPerson_for_amity_administrator(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': self.user.email, 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_permission_class_IsAmityAdministratorOrCommunityContactPerson_for_supervisor_is_contact_person(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': self.user1.email, 'password': 'user1'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_permission_class_IsAmityAdministratorOrCommunityContactPerson_for_supervisor_is_not_contact_person(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': self.user2.email, 'password': 'user2'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
