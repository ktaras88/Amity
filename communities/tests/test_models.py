from rest_framework.test import APITestCase

from communities.models import Community
from users.models import User


class TestCommunitiesModel(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(email='super@super.super', password='1234',
                                                  first_name='First', last_name='Last')

    def test_create_community(self):
        community = Community.objects.create(name='Community', state='AL', zip_code=1234, address='1, address',
                                             contact_person=self.user, phone_number=1234567, safety_status=True)
        self.assertEqual(community.name, 'Community')
        self.assertEqual(community.state, 'AL')
        self.assertEqual(community.zip_code, 1234)
        self.assertEqual(community.address, '1, address')
        self.assertEqual(community.contact_person, self.user)
        self.assertEqual(community.phone_number, 1234567)
        self.assertEqual(community.safety_status, True)
