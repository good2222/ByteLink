from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Post, Comment, Like

User = get_user_model()

class PostTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='password123'
        )
        self.other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='password123'
        )
        self.client.login(username='author', password='password123')

    def test_create_post(self):
        url = reverse('post_create')
        response = self.client.post(url, {'content': 'Hello, world!'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.content, 'Hello, world!')
        self.assertEqual(post.author, self.user)

    def test_delete_post_by_author(self):
        post = Post.objects.create(author=self.user, content='Delete me')
        delete_url = reverse('post_delete', kwargs={'pk': post.pk})
        response = self.client.post(delete_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), 0)

    def test_like_toggle(self):
        post = Post.objects.create(author=self.user, content='Like me')
        like_url = reverse('post_like', kwargs={'pk': post.pk})
        
        # Like
        response = self.client.post(like_url, follow=True)
        self.assertEqual(post.likes_count, 1)
        self.assertTrue(post.is_liked_by(self.user))

        # Unlike
        response = self.client.post(like_url, follow=True)
        self.assertEqual(post.likes_count, 0)
        self.assertFalse(post.is_liked_by(self.user))

    def test_create_comment(self):
        post = Post.objects.create(author=self.user, content='Comment on me')
        comment_url = reverse('comment_create', kwargs={'pk': post.pk})
        response = self.client.post(comment_url, {'text': 'Nice post!'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post.comments.count(), 1)
        self.assertEqual(post.comments.first().text, 'Nice post!')
