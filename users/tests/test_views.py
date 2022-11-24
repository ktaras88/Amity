import tempfile
from PIL import Image
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from buildings.models import Building
from communities.models import Community
from users.choices_types import ProfileRoles
from users.models import InvitationToken, Profile

User = get_user_model()


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
    def setUp(self):
        self.user = User.objects.create_superuser(email='super@super.super', password='strong')
        self.url = f'/api/v1.0/users/{self.user.id}/avatar/'

        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)
        tmp_file.seek(0)

        self.data = {'avatar': tmp_file, 'avatar_coord': 100}

    def test_get_data_for_authenticated_client(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_data_for_un_authenticated_client(self):
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ensure_avatar_and_coord_recorded(self):
        response = self.client.put(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['avatar'])
        self.assertTrue(response.data['avatar_coord'])

    def test_delete_avatar_and_coord(self):
        self.client.put(self.url, self.data)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ResetPasswordRequestEmailTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('v1.0:users:forgot-password')
        self.user = User.objects.create_user(email='user@user.user')

    def test_forgot_password_email_not_in_the_system(self):
        data = {'email': 'no@no.no'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'There is no account with that email.')

    def test_forgot_password_email_in_the_system_check_response(self):
        data = {'email': self.user.email}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(User.objects.get(email=self.user.email).security_code), 6)

    def test_forgot_password_if_request_data_is_empty(self):
        data = {}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'This field is required.')


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
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'There is no user with that email.')

    def test_security_code_wrong_code(self):
        data = {'email': self.user.email, 'security_code': '000000'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'],
                         'Incorrect security code. Check your secure code or request for a new one.')

    def test_security_code_generate_token(self):
        data = {'email': self.user.email, 'security_code': self.user.security_code}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        self.assertEqual(len(mail.outbox), 1)

    def test_security_code_empty_data(self):
        data = {}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'This field is required.')
        self.assertEqual(response.data['security_code'][0], 'This field is required.')


class CreateNewPasswordTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('v1.0:users:create-new-password')
        self.user = User.objects.create_user(email='user@user.user')
        self.token = str(InvitationToken.objects.filter(user=self.user).first())

    def test_create_new_password_add_email_field(self):
        data = {'token': self.token, 'password': 'User-password123', 'confirm_password': 'User-password123'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_create_new_password_wrong_token(self):
        data = {'token': 'wrong-token', 'password': 'User-password123', 'confirm_password': 'User-password123'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'][0], 'Invalid token.')

    def test_create_new_password_compare_passwords_not_the_same(self):
        data = {'token': self.token, 'password': 'User-password123', 'confirm_password': 'User-password321'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'][0], 'Passwords do not match.')

    def test_create_new_password_correct(self):
        data = {'token': self.token, 'password': 'User-password123', 'confirm_password': 'User-password123'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.user.password == data['password'])

    def test_create_new_password_empty_data(self):
        data = {}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['token'][0], 'This field is required.')
        self.assertEqual(response.data['password'][0], 'This field is required.')
        self.assertEqual(response.data['confirm_password'][0], 'This field is required.')

    def test_create_new_password_after_successful_request_token_was_removed_from_the_system(self):
        data = {'token': self.token, 'password': 'User-password123', 'confirm_password': 'User-password123'}
        self.assertTrue(InvitationToken.objects.filter(user=self.user).exists())
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(InvitationToken.objects.filter(user=self.user).exists())
        user = User.objects.get(id=self.user.id)
        self.assertTrue(user.check_password(data['password']))

    def test_ensure_password_is_valid(self):
        data = {'token': self.token, 'password': '12Jsirvm&*knv4', 'confirm_password': '12Jsirvm&*knv4'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ensure_minimum_length_is_invalid(self):
        data = {'token': self.token, 'password': '12Jsir*', 'confirm_password': '12Jsir*'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0],
                         "This password is too short. It must contain at least %d characters." % 8)

    def test_ensure_maximum_length_is_invalid(self):
        data = {'token': self.token,
                'password': '12Jsir*rvsdbhrthnngfnewrvsdcge1346tfsedfvtjFhmhgwsgsnrsegbgfnryyzetahdnzfmtusjehfnfjysruaengdngkdjahthfxthysykysjtdfbfdbfgtjhtrsjsrysmy6',
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


class UserProfileInformationTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(email='super@super.super', password='strong',
                                                  first_name='Fsuper', last_name='Lastsuper')
        self.url = reverse('v1.0:users:profile-info', args=[self.user.id])
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'super@super.super',
                                                                   'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

        self.user1 = User.objects.create_user(email='mark@hamill.act', password='M@rkHami11',
                                              first_name='Mark', last_name='Spencer')

    def test_ensure_first_name_last_name_phone_number_are_valid(self):
        data = {'first_name': 'Mark', 'last_name': 'Hamill', 'phone_number': '0669853245'}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ensure_first_name_not_blank(self):
        data = {'first_name': '', 'last_name': 'Hamill'}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['first_name'][0], "This field may not be blank.")

    def test_ensure_last_name_not_blank(self):
        data = {'first_name': 'Mark', 'last_name': ''}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['last_name'][0], "This field may not be blank.")

    def test_ensure_first_name_above_100_symbols_fails(self):
        data = {
            'first_name': 'MarkmarkmarkmarkmarkmarkmarkmarkmarkmarkmarkmarkmarkmarkmarkmarkmarkmarkmarkmarkmarkmarkmarkmarkmarkMarkmark',
            'last_name': 'Hamill'}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['first_name'][0], "Ensure this field has no more than 100 characters.")

    def test_ensure_last_name_above_100_symbols_fails(self):
        data = {
            'first_name': 'Mark',
            'last_name': 'Hamillhamillhamillhamillhamillhamillhamillhamillhamillhamillhamillhamillhamillhamillhamillhamillhamillhamillhamill'}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['last_name'][0], "Ensure this field has no more than 100 characters.")

    def test_ensure_phone_number_above_20_symbols_fails(self):
        data = {'phone_number': '0958552153095855215334'}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['phone_number'][0], "Phone number must be entered in the format: "
                                                           "'+999999999'. Up to 15 digits allowed.")


class UserPasswordInformationTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(email='super@super.super', password='strong',
                                                  first_name='Fsuper', last_name='Lastsuper')
        self.url = reverse('v1.0:users:user-password-info', args=[self.user.id])
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'super@super.super', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

        self.user1 = User.objects.create_user(email='jim@parsons.art', password='j1mp@Rs*ns',
                                              first_name='Jim', last_name='Parsons')

    def test_ensure_password_change_is_valid(self):
        data = {'old_password': 'strong', 'password': '12Jsirvm&*knv4', 'password2': '12Jsirvm&*knv4'}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ensure_old_password_is_invalid(self):
        data = {'old_password': 'strong133', 'password': '12Jsirvm&*knv4', 'password2': '12Jsirvm&*knv4'}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['old_password']['old_password'], "Old password is not correct")

    def test_ensure_new_password_and_password_repeat_not_same(self):
        data = {'old_password': 'strong', 'password': '12Jsirvm&*kn', 'password2': '12Jsirvm&*k'}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], 'Password fields didn\'t match.')


class UsersRoleListAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(email='super@super.super', password='strong',
                                                  first_name='Fsuper', last_name='Lastsuper')
        self.user1 = User.objects.create_user(email='user1@user.com', password='strong',
                                              first_name='First User1', last_name='Last User2',
                                              role=ProfileRoles.SUPERVISOR)
        self.user2 = User.objects.create_user(email='user2@user.com', password='strong',
                                              first_name='First User2', last_name='BBB',
                                              role=ProfileRoles.SUPERVISOR)
        self.user3 = User.objects.create_user(email='user3@user.com', password='strong',
                                              first_name='First User3', last_name='Last User3',
                                              role=ProfileRoles.COORDINATOR)
        self.user4 = User.objects.create_user(email='user4@user.com', password='strong',
                                              first_name='First User4', last_name='Last User4',
                                              role=ProfileRoles.COORDINATOR)
        self.user5 = User.objects.create_user(email='user5@user.com', password='strong',
                                              first_name='First User5', last_name='Last User5',
                                              role=ProfileRoles.COORDINATOR)
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'super@super.super',
                                                                   'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_list_of_users_by_role_supervisor(self):
        self.url = reverse('v1.0:users:users-role-list', args=['supervisor'])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)

    def test_list_of_users_by_role_coordinator(self):
        self.url = reverse('v1.0:users:users-role-list', args=['coordinator'])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 3)

    def test_list_of_users_by_role_observer_empty_list(self):
        self.url = reverse('v1.0:users:users-role-list', args=['observer'])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 0)

    def test_list_of_users_by_role_incorrect_role_name(self):
        self.url = reverse('v1.0:users:users-role-list', args=['user'])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class NewMemberAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(email='super@super.super', password='strong',
                                                  first_name='Fsuper', last_name='Lastsuper')
        self.user1 = User.objects.create_user(email='user1@user.com', password='strong1',
                                              first_name='First User1', last_name='Last User1',
                                              role=ProfileRoles.SUPERVISOR)
        self.user2 = User.objects.create_user(email='user2@user.com', password='strong2',
                                              first_name='First User2', last_name='Last User2',
                                              role=ProfileRoles.OBSERVER)
        self.com = Community.objects.create(name='Davida', state='DC', zip_code=1111, address='davida_address',
                                            phone_number=1230456204, safety_status=True)
        self.build1 = Building.objects.create(community_id=self.com.id, name='building1', state='DC',
                                              address='address1', contact_person=self.user2, phone_number=1234567)
        self.build2 = Building.objects.create(community_id=self.com.id, name='building2', state='DC',
                                              address='address2', phone_number=7654321)
        self.build3 = Building.objects.create(community_id=self.com.id, name='building3', state='DC',
                                              address='address3', phone_number=7654321)

        self.url = reverse('v1.0:users:create-new-member')

        self.data = {
            'email': 'site.vizit@gmail.com',
            'first_name': 'First User3',
            'last_name': 'Last User3',
            'address': 'User address',
        }

        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'super@super.super', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_create_new_member_permission_no_access_for_observer(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user2@user.com', 'password': 'strong2'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_new_member_permission_access_for_supervizor_created_without_member_property(self):
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'user1@user.com', 'password': 'strong1'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        self.data.update({'role': ProfileRoles.SUPERVISOR})
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(email=self.data['email']).count(), 1)
        self.assertEqual(Profile.objects.filter(user__email=self.data['email']).count(), 1)
        self.assertEqual(Profile.objects.get(user__email=self.data['email']).role, ProfileRoles.SUPERVISOR)
        self.assertEqual(Building.objects.filter(contact_person__email=self.data['email']).count(), 0)

    def test_create_new_member_permission_access_for_amity_admin_created_with_member_property(self):
        self.data.update({
            'role': ProfileRoles.COORDINATOR,
            'property': self.build2.id
        })
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(email=self.data['email']).count(), 1)
        self.assertEqual(Profile.objects.filter(user__email=self.data['email']).count(), 1)
        self.assertEqual(Profile.objects.get(user__email=self.data['email']).role, ProfileRoles.COORDINATOR)
        self.assertEqual(Building.objects.filter(contact_person__email=self.data['email']).count(), 1)

    def test_create_new_member_permission_access_for_amity_admin_no_role_error(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['role'][0], 'This field is required.')


class ActivateAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(email='admin@admin.admin', password='strong',
                                                  first_name='First-super', last_name='Last-super')
        self.user1 = User.objects.create_user(email='user01@user1.user1', password='M@rkHami11',
                                              first_name='Mark', last_name='Hamill',
                                              role=ProfileRoles.COORDINATOR)
        self.com = Community.objects.create(name='Davida', state='AZ', zip_code=1111, address='davida_address',
                                            contact_person=self.user1, phone_number=1230456204, safety_status=True)
        self.build1 = Building.objects.create(community_id=self.com.id, name='building1', state='AZ',
                                              address='address1', contact_person=self.user1, phone_number=1234567)
        self.url = reverse('v1.0:users:activate-member', kwargs={'pk': self.user1.id})
        self.client = APIClient()
        res = self.client.post(reverse('v1.0:token_obtain_pair'), {'email': 'admin@admin.admin', 'password': 'strong'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_activation_user(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_active'], User.objects.get(id=self.user1.id).is_active)

    def test_activation_without_permission_not_work(self):
        user10 = User.objects.create_user(email='user010@user10.user10', password='M@rkHami100',
                                          first_name='Mark00', last_name='Hamill00',
                                          role=ProfileRoles.RESIDENT)
        client = APIClient()
        res = client.post(reverse('v1.0:token_obtain_pair'),
                          {'email': 'user010@user10.user10', 'password': 'M@rkHami100'})
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

        url = reverse('v1.0:users:activate-member', kwargs={'pk': user10.id})
        response = client.put(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')
