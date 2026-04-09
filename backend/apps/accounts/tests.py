from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import User


class TestUserModel(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email='agent@test.com',
            password='TestP@ss1',
            first_name='John',
            last_name='Doe',
        )
        self.assertEqual(user.email, 'agent@test.com')
        self.assertEqual(user.role, 'agent')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.check_password('TestP@ss1'))

    def test_create_user_normalizes_email(self):
        user = User.objects.create_user(
            email='Test@EXAMPLE.COM',
            password='TestP@ss1',
            first_name='A',
            last_name='B',
        )
        self.assertEqual(user.email, 'Test@example.com')

    def test_create_user_without_email_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='TestP@ss1', first_name='A', last_name='B')

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email='super@test.com',
            password='TestP@ss1',
            first_name='Super',
            last_name='User',
        )
        self.assertEqual(user.role, 'superuser')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_full_name(self):
        user = User(first_name='Jane', last_name='Doe')
        self.assertEqual(user.full_name, 'Jane Doe')

    def test_str(self):
        user = User(email='test@test.com')
        self.assertEqual(str(user), 'test@test.com')


class AuthEndpointTestBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.superuser = User.objects.create_superuser(
            email='super@test.com',
            password='SuperP@ss1',
            first_name='Super',
            last_name='User',
        )
        self.admin = User.objects.create_user(
            email='admin@test.com',
            password='AdminP@ss1',
            first_name='Admin',
            last_name='User',
            role='admin',
        )
        self.agent = User.objects.create_user(
            email='agent@test.com',
            password='AgentP@ss1',
            first_name='Agent',
            last_name='User',
        )

    def login_as(self, email, password):
        response = self.client.post('/api/accounts/auth/login/', {
            'email': email,
            'password': password,
        })
        tokens = response.data
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        return tokens


class TestLogin(AuthEndpointTestBase):
    def test_login_success(self):
        response = self.client.post('/api/accounts/auth/login/', {
            'email': 'admin@test.com',
            'password': 'AdminP@ss1',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['role'], 'admin')

    def test_superuser_login(self):
        response = self.client.post('/api/accounts/auth/login/', {
            'email': 'super@test.com',
            'password': 'SuperP@ss1',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['role'], 'superuser')

    def test_login_invalid_credentials(self):
        response = self.client.post('/api/accounts/auth/login/', {
            'email': 'admin@test.com',
            'password': 'wrong',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestTokenRefresh(AuthEndpointTestBase):
    def test_refresh_token(self):
        tokens = self.login_as('admin@test.com', 'AdminP@ss1')
        response = self.client.post('/api/accounts/auth/refresh/', {
            'refresh': tokens['refresh'],
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class TestLogout(AuthEndpointTestBase):
    def test_logout_success(self):
        tokens = self.login_as('admin@test.com', 'AdminP@ss1')
        response = self.client.post('/api/accounts/auth/logout/', {
            'refresh': tokens['refresh'],
        })
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_logout_blacklists_token(self):
        tokens = self.login_as('admin@test.com', 'AdminP@ss1')
        self.client.post('/api/accounts/auth/logout/', {
            'refresh': tokens['refresh'],
        })
        response = self.client.post('/api/accounts/auth/refresh/', {
            'refresh': tokens['refresh'],
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_without_refresh_token(self):
        self.login_as('admin@test.com', 'AdminP@ss1')
        response = self.client.post('/api/accounts/auth/logout/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestUserCreate(AuthEndpointTestBase):
    def test_admin_can_create_user(self):
        self.login_as('admin@test.com', 'AdminP@ss1')
        response = self.client.post('/api/accounts/users/create/', {
            'email': 'newuser@test.com',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'staff',
            'password': 'NewP@ssw0rd',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@test.com').exists())

    def test_superuser_can_create_user(self):
        self.login_as('super@test.com', 'SuperP@ss1')
        response = self.client.post('/api/accounts/users/create/', {
            'email': 'newuser@test.com',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'agent',
            'password': 'NewP@ssw0rd',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_create_superuser_role(self):
        self.login_as('super@test.com', 'SuperP@ss1')
        response = self.client.post('/api/accounts/users/create/', {
            'email': 'fake@test.com',
            'first_name': 'Fake',
            'last_name': 'Super',
            'role': 'superuser',
            'password': 'FakeP@ssw0rd',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_agent_cannot_create_user(self):
        self.login_as('agent@test.com', 'AgentP@ss1')
        response = self.client.post('/api/accounts/users/create/', {
            'email': 'hack@test.com',
            'first_name': 'Hack',
            'last_name': 'User',
            'role': 'admin',
            'password': 'HackP@ssw0rd',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_weak_password_rejected(self):
        self.login_as('admin@test.com', 'AdminP@ss1')
        response = self.client.post('/api/accounts/users/create/', {
            'email': 'weak@test.com',
            'first_name': 'Weak',
            'last_name': 'User',
            'role': 'agent',
            'password': 'abc',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestUserList(AuthEndpointTestBase):
    def test_admin_can_list_users(self):
        self.login_as('admin@test.com', 'AdminP@ss1')
        response = self.client.get('/api/accounts/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        emails = [u['email'] for u in response.data]
        self.assertIn('admin@test.com', emails)
        self.assertIn('agent@test.com', emails)
        self.assertNotIn('super@test.com', emails)

    def test_superuser_not_in_list(self):
        self.login_as('super@test.com', 'SuperP@ss1')
        response = self.client.get('/api/accounts/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        roles = [u['role'] for u in response.data]
        self.assertNotIn('superuser', roles)

    def test_agent_cannot_list_users(self):
        self.login_as('agent@test.com', 'AgentP@ss1')
        response = self.client.get('/api/accounts/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestProfile(AuthEndpointTestBase):
    def test_get_own_profile(self):
        self.login_as('agent@test.com', 'AgentP@ss1')
        response = self.client.get('/api/accounts/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'agent@test.com')

    def test_update_profile(self):
        self.login_as('agent@test.com', 'AgentP@ss1')
        response = self.client.patch('/api/accounts/profile/', {
            'first_name': 'Updated',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.agent.refresh_from_db()
        self.assertEqual(self.agent.first_name, 'Updated')

    def test_cannot_change_role_via_profile(self):
        self.login_as('agent@test.com', 'AgentP@ss1')
        self.client.patch('/api/accounts/profile/', {
            'role': 'admin',
        })
        self.agent.refresh_from_db()
        self.assertEqual(self.agent.role, 'agent')

    def test_unauthenticated_cannot_access_profile(self):
        response = self.client.get('/api/accounts/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestUserDetail(AuthEndpointTestBase):
    def test_admin_can_retrieve_user(self):
        self.login_as('admin@test.com', 'AdminP@ss1')
        response = self.client.get(f'/api/accounts/users/{self.agent.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'agent@test.com')

    def test_admin_can_update_user(self):
        self.login_as('admin@test.com', 'AdminP@ss1')
        response = self.client.patch(
            f'/api/accounts/users/{self.agent.pk}/',
            {'first_name': 'Changed'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.agent.refresh_from_db()
        self.assertEqual(self.agent.first_name, 'Changed')

    def test_admin_can_change_role(self):
        self.login_as('admin@test.com', 'AdminP@ss1')
        response = self.client.patch(
            f'/api/accounts/users/{self.agent.pk}/',
            {'role': 'staff'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.agent.refresh_from_db()
        self.assertEqual(self.agent.role, 'staff')

    def test_cannot_assign_superuser_role(self):
        self.login_as('admin@test.com', 'AdminP@ss1')
        response = self.client.patch(
            f'/api/accounts/users/{self.agent.pk}/',
            {'role': 'superuser'},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_can_deactivate_user(self):
        self.login_as('admin@test.com', 'AdminP@ss1')
        response = self.client.patch(
            f'/api/accounts/users/{self.agent.pk}/',
            {'is_active': False},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.agent.refresh_from_db()
        self.assertFalse(self.agent.is_active)

    def test_superuser_not_accessible_via_detail(self):
        self.login_as('admin@test.com', 'AdminP@ss1')
        response = self.client.get(f'/api/accounts/users/{self.superuser.pk}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_agent_cannot_access_user_detail(self):
        self.login_as('agent@test.com', 'AgentP@ss1')
        response = self.client.get(f'/api/accounts/users/{self.admin.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_user(self):
        self.login_as('admin@test.com', 'AdminP@ss1')
        agent_pk = self.agent.pk
        response = self.client.delete(f'/api/accounts/users/{agent_pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=agent_pk).exists())

    def test_cannot_delete_superuser(self):
        self.login_as('admin@test.com', 'AdminP@ss1')
        response = self.client.delete(f'/api/accounts/users/{self.superuser.pk}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_delete_self(self):
        self.login_as('admin@test.com', 'AdminP@ss1')
        response = self.client.delete(f'/api/accounts/users/{self.admin.pk}/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(User.objects.filter(pk=self.admin.pk).exists())

    def test_agent_cannot_delete_user(self):
        self.login_as('agent@test.com', 'AgentP@ss1')
        response = self.client.delete(f'/api/accounts/users/{self.admin.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_nonexistent_user_returns_404(self):
        self.login_as('admin@test.com', 'AdminP@ss1')
        response = self.client.get('/api/accounts/users/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestPasswordChange(AuthEndpointTestBase):
    def test_change_password_success(self):
        self.login_as('agent@test.com', 'AgentP@ss1')
        response = self.client.post('/api/accounts/profile/password/', {
            'old_password': 'AgentP@ss1',
            'new_password': 'NewP@ssw0rd',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.agent.refresh_from_db()
        self.assertTrue(self.agent.check_password('NewP@ssw0rd'))

    def test_wrong_old_password(self):
        self.login_as('agent@test.com', 'AgentP@ss1')
        response = self.client.post('/api/accounts/profile/password/', {
            'old_password': 'WrongP@ss1',
            'new_password': 'NewP@ssw0rd',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_weak_new_password(self):
        self.login_as('agent@test.com', 'AgentP@ss1')
        response = self.client.post('/api/accounts/profile/password/', {
            'old_password': 'AgentP@ss1',
            'new_password': 'weak',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_cannot_change_password(self):
        response = self.client.post('/api/accounts/profile/password/', {
            'old_password': 'AgentP@ss1',
            'new_password': 'NewP@ssw0rd',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
