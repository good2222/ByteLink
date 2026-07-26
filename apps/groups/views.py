from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count

from .models import Group, GroupMembership
from .forms import GroupForm
from apps.posts.models import Post
from apps.posts.forms import PostForm, CommentForm


class GroupListView(ListView):
    model = Group
    template_name = 'groups/group_list.html'
    context_object_name = 'groups'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '').strip()
        if self.request.user.is_authenticated:
            # Мои группы (где я состою)
            context['my_groups'] = Group.objects.filter(memberships__user=self.request.user)
        return context


class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    form_class = GroupForm
    template_name = 'groups/group_create.html'

    def form_valid(self, form):
        form.instance.creator = self.request.user
        response = super().form_valid(form)
        # Автоматически делаем создателя админом группы
        GroupMembership.objects.create(group=self.object, user=self.request.user, role='admin')
        return response

    def get_success_url(self):
        return reverse_lazy('group_detail', kwargs={'pk': self.object.pk})


class GroupDetailView(DetailView):
    model = Group
    template_name = 'groups/group_detail.html'
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_object()
        user = self.request.user

        # Формы постов и комментариев
        context['post_form'] = PostForm()
        context['comment_form'] = CommentForm()

        # Посты группы
        group_posts = (
            group.posts
            .select_related('author')
            .prefetch_related('likes', 'comments__author')
            .annotate(like_count=Count('likes'))
            .order_by('-created_at')
        )
        if user.is_authenticated:
            for post in group_posts:
                post.is_liked = post.is_liked_by(user)

        context['posts'] = group_posts

        # Все участники группы
        memberships = group.memberships.select_related('user').all()
        context['memberships'] = memberships

        is_member = False
        user_role = None

        if user.is_authenticated:
            curr = memberships.filter(user=user).first()
            if curr:
                is_member = True
                user_role = curr.role

        context['is_member'] = is_member
        context['user_role'] = user_role
        context['is_group_admin'] = user_role in ['admin', 'moderator'] or group.creator == user
        return context


class GroupJoinToggleView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        group = get_object_or_404(Group, pk=pk)
        membership = GroupMembership.objects.filter(user=request.user, group=group).first()

        if membership:
            # Создатель группы не может случайно её покинуть таким образом
            if group.creator != request.user:
                membership.delete()
        else:
            GroupMembership.objects.create(
                user=request.user,
                group=group,
                role='member'
            )

        return redirect('group_detail', pk=group.pk)


class GroupEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Group
    form_class = GroupForm
    template_name = 'groups/group_edit.html'

    def test_func(self):
        group = self.get_object()
        user = self.request.user
        membership = group.memberships.filter(user=user).first()
        return group.creator == user or (membership and membership.role in ['admin', 'moderator']) or user.is_site_admin

    def get_success_url(self):
        return reverse_lazy('group_detail', kwargs={'pk': self.object.pk})


class GroupDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Group
    success_url = reverse_lazy('group_list')

    def test_func(self):
        group = self.get_object()
        user = self.request.user
        return group.creator == user or user.is_site_admin