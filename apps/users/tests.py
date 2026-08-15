from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User',
            role='user'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'user')
        self.assertFalse(user.is_site_admin)
        self.assertEqual(str(user), 'testuser')

    def test_create_first_user_as_admin(self):
        url = reverse('register')
        data = {
            'username': 'adminuser',
            'email': 'admin@example.com',
            'password1': 'adminpassword123',
            'password2': 'adminpassword123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        
        user = User.objects.get(username='adminuser')
        self.assertEqual(user.role, 'admin')
        self.assertTrue(user.is_site_admin)

class UserViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='johndoe',
            email='john@example.com',
            password='password123',
            first_name='John',
            last_name='Doe'
        )
        self.client.login(username='johndoe', password='password123')

    def test_home_page_accessible(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_profile_page_accessible(self):
        response = self.client.get(reverse('profile', kwargs={'username': 'johndoe'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')
        self.assertContains(response, 'John Doe')

    def test_profile_edit(self):
        edit_url = reverse('profile_edit')
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 200)
        data = {
            'first_name': 'Johnny',
            'last_name': 'Doe',
            'bio': 'Updated bio description',
            'status_message': 'Feeling coding vibe',
            'location': 'Kyiv, Ukraine',
            'website': 'https://johnny.dev'
        }
        response = self.client.post(edit_url, data)
        self.assertEqual(response.status_code, 302) 
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Johnny')
        self.assertEqual(self.user.bio, 'Updated bio description')
        self.assertEqual(self.user.status_message, 'Feeling coding vibe')
        self.assertEqual(self.user.location, 'Kyiv, Ukraine')
        self.assertEqual(self.user.website, 'https://johnny.dev')
