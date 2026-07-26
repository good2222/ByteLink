from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView, View, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.db.models import Count, Q
from django.contrib import messages

from .models import CustomUser, FriendRequest
from .forms import CustomUserCreationForm, UserProfileForm
from apps.posts.models import Post
from apps.posts.forms import PostForm, CommentForm


class RegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
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

        friends = self.request.user.get_friends()

        posts = (
            Post.objects
            .select_related('author')
            .prefetch_related('likes', 'comments__author')
            .filter(Q(author=self.request.user) | Q(author__in=friends))
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

        posts = (
            self.object.posts
            .select_related('author')
            .prefetch_related('likes', 'comments__author')
            .annotate(like_count=Count('likes'))
            .order_by('-like_count', '-created_at')
        )
        for post in posts:
            post.is_liked = post.is_liked_by(self.request.user)
        context['user_posts'] = posts
        context['is_own_profile'] = self.object == self.request.user
        context['friends'] = self.object.get_friends()[:6]  
        context['friends_count'] = self.object.get_friends().count()

        if not context['is_own_profile']:
            me = self.request.user
            other = self.object
            req = FriendRequest.objects.filter(
                Q(from_user=me, to_user=other) | Q(from_user=other, to_user=me)
            ).first()
            context['friend_request'] = req
            if req:
                context['are_friends'] = req.status == 'accepted'
                context['request_pending_sent'] = req.status == 'pending' and req.from_user == me
                context['request_pending_received'] = req.status == 'pending' and req.to_user == me
            else:
                context['are_friends'] = False
                context['request_pending_sent'] = False
                context['request_pending_received'] = False

        return context



class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'username': self.request.user.username})


class UserSearchView(LoginRequiredMixin, ListView):
    template_name = 'users/search.html'
    context_object_name = 'results'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query:
            return CustomUser.objects.none()
        return (
            CustomUser.objects
            .filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            )
            .exclude(pk=self.request.user.pk)
            .order_by('username')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class FriendsListView(LoginRequiredMixin, View):
    def get(self, request, username=None):
        if username:
            profile_user = get_object_or_404(CustomUser, username=username)
        else:
            profile_user = request.user
        friends = profile_user.get_friends()
        return render(request, 'users/friends.html', {
            'profile_user': profile_user,
            'friends': friends,
        })


class FriendRequestsView(LoginRequiredMixin, View):
    def get(self, request):
        incoming = FriendRequest.objects.filter(
            to_user=request.user, status='pending'
        ).select_related('from_user').order_by('-created_at')
        return render(request, 'users/friend_requests.html', {
            'incoming': incoming,
        })


class SendFriendRequestView(LoginRequiredMixin, View):
    def post(self, request, username):
        to_user = get_object_or_404(CustomUser, username=username)
        if to_user == request.user:
            messages.error(request, 'Нельзя добавить себя в друзья.')
            return redirect('profile', username=username)

        existing = FriendRequest.objects.filter(
            Q(from_user=request.user, to_user=to_user) |
            Q(from_user=to_user, to_user=request.user)
        ).first()

        if existing:
            if existing.status == 'declined' and existing.from_user == request.user:
                existing.status = 'pending'
                existing.save()
                messages.success(request, f'Заявка отправлена пользователю {to_user.username}.')
            else:
                messages.info(request, 'Заявка уже существует.')
        else:
            FriendRequest.objects.create(from_user=request.user, to_user=to_user)
            messages.success(request, f'Заявка отправлена пользователю {to_user.username}.')

        return redirect('profile', username=username)

class AcceptFriendRequestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        freq = get_object_or_404(FriendRequest, pk=pk, to_user=request.user, status='pending')
        freq.status = 'accepted'
        freq.save()
        messages.success(request, f'Вы приняли заявку от {freq.from_user.username}.')
        return redirect(request.META.get('HTTP_REFERER', 'friend_requests'))


class DeclineFriendRequestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        freq = get_object_or_404(FriendRequest, pk=pk, to_user=request.user, status='pending')
        freq.status = 'declined'
        freq.save()
        messages.info(request, f'Заявка от {freq.from_user.username} отклонена.')
        return redirect(request.META.get('HTTP_REFERER', 'friend_requests'))


class RemoveFriendView(LoginRequiredMixin, View):
    def post(self, request, username):
        other = get_object_or_404(CustomUser, username=username)
        FriendRequest.objects.filter(
            Q(from_user=request.user, to_user=other) |
            Q(from_user=other, to_user=request.user)
        ).delete()
        messages.success(request, f'{other.username} удалён из друзей.')
        return redirect('profile', username=username)
