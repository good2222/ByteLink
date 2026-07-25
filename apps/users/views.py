from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from django.db.models import Count

from .models import CustomUser
from .forms import CustomUserCreationForm, UserProfileForm
from apps.posts.models import Post
from apps.posts.forms import PostForm, CommentForm

class RegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # Automatically log in the user after successful registration
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_form'] = PostForm()
        context['comment_form'] = CommentForm()
        # annotate — добавляет виртуальное поле like_count = количество лайков каждого поста
        # order_by('-like_count', '-created_at') — сначала самые популярные, при равенстве — новые
        posts = (
            Post.objects
            .select_related('author')
            .prefetch_related('likes', 'comments__author')
            .annotate(like_count=Count('likes'))
            .order_by('-like_count', '-created_at')
        )
        for post in posts:
            post.is_liked = post.is_liked_by(self.request.user)
        context['feed_posts'] = posts
        return context

class ProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_form'] = PostForm()
        context['comment_form'] = CommentForm()
        
        posts = self.object.posts.select_related('author').prefetch_related('likes', 'comments__author').all()
        for post in posts:
            post.is_liked = post.is_liked_by(self.request.user)
            
        context['user_posts'] = posts
        context['is_own_profile'] = self.object == self.request.user
        return context

class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    
    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'username': self.request.user.username})
