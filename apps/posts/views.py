from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Post, Comment, Like
from .forms import PostForm, CommentForm
from apps.notifications.models import Notification


def send_notification_ws(recipient, sender, message, post=None, notif_type='like'):
    """Отправляет push-уведомление через WebSockets в реальном времени."""
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f'user_{recipient.id}',
            {
                'type': 'new_message_notification',
                'message': message,
                'sender_username': sender.username,
                'sender_avatar': sender.get_avatar_url,
                'post_id': post.id if post else 0
            }
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.author = self.request.user
        group_id = self.request.POST.get('group_id')
        if group_id:
            form.instance.group_id = group_id
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', reverse_lazy('home'))


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_site_admin

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', reverse_lazy('home'))


class LikeToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        like, created = Like.objects.get_or_create(post=post, user=request.user)

        if not created:
            like.delete()
            liked = False
            Notification.objects.filter(
                recipient=post.author,
                sender=request.user,
                notification_type='like',
                post=post
            ).delete()
        else:
            liked = True
            if post.author != request.user:
                Notification.objects.get_or_create(
                    recipient=post.author,
                    sender=request.user,
                    notification_type='like',
                    post=post
                )
                send_notification_ws(
                    recipient=post.author,
                    sender=request.user,
                    message=f'{request.user.username} поставил(а) лайк вашему посту.',
                    post=post,
                    notif_type='like'
                )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'liked': liked,
                'count': post.likes.count()
            })

        return redirect(request.META.get('HTTP_REFERER', 'home'))


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        form.instance.post = post
        form.instance.author = self.request.user
        response = super().form_valid(form)

        if post.author != self.request.user:
            Notification.objects.create(
                recipient=post.author,
                sender=self.request.user,
                notification_type='comment',
                post=post
            )
            send_notification_ws(
                recipient=post.author,
                sender=self.request.user,
                message=f'{self.request.user.username} оставил(а) комментарий к вашему посту.',
                post=post,
                notif_type='comment'
            )

        return response

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', reverse_lazy('home'))


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment

    def test_func(self):
        comment = self.get_object()
        return (
            self.request.user == comment.author or
            self.request.user == comment.post.author or
            self.request.user.is_site_admin
        )

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', reverse_lazy('home'))
