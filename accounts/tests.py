from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class PasswordChangeTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='oldpassword123'
        )
        self.password_change_url = '/account/change-password/'
        
    def test_authenticated_password_change_success(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newsecurepassword123',
            'new_password2': 'newsecurepassword123'
        }
        response = self.client.put(
            self.password_change_url,
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password updated successfully')
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newsecurepassword123'))

    def test_authenticated_password_change_wrong_old_password(self):
        """Test password change with wrong old password"""
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newsecurepassword123',
            'new_password2': 'newsecurepassword123'
        }
        response = self.client.put(
            self.password_change_url,
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', response.data)

    def test_unauthenticated_password_change(self):
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newsecurepassword123',
            'new_password2': 'newsecurepassword123'
        }
        response = self.client.put(
            self.password_change_url,
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)