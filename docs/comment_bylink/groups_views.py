# ============================================================
# ФАЙЛ: apps/groups/views.py
# Обработчики страниц для работы с группами (сообществами)
# ============================================================

# render — рендеринг шаблона с данными
# redirect — редирект на другой URL
# get_object_or_404 — получить объект из БД или вернуть ошибку 404 если не найден
from django.shortcuts import render, redirect, get_object_or_404

# reverse_lazy — построение URL-адреса по имени маршрута
from django.urls import reverse_lazy

# Классовые представления Django:
# ListView   — список объектов (каталог групп)
# DetailView — детали одного объекта (страница группы)
# CreateView — создание объекта через форму (создание группы)
# UpdateView — редактирование объекта через форму (настройки группы)
# DeleteView — удаление объекта (удаление группы)
# View       — базовый класс (для обработки POST-запросов)
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View

# LoginRequiredMixin — доступ только для авторизованных пользователей
# UserPassesTestMixin — доступ только при выполнении проверки прав (например, только для админа)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Q — класс для сложных SQL-условий (ИЛИ / И)
# Count — функция агрегации (подсчёт лайков)
from django.db.models import Q, Count

# Модели группы и участников
from .models import Group, GroupMembership

# Форма создания/редактирования группы
from .forms import GroupForm

# Модели и формы постов для отображения стены постов группы
from apps.posts.models import Post
from apps.posts.forms import PostForm, CommentForm


# ============================================================
# VIEW: GroupListView — Каталог групп (/groups/)
# Отображает список всех доступных групп и результаты поиска
# ============================================================
class GroupListView(ListView):
    # Модель с которой работаем
    model = Group
    # HTML-шаблон каталога
    template_name = 'groups/group_list.html'
    # Имя списка в шаблоне: {% for g in groups %}
    context_object_name = 'groups'
    # Количество групп на одной странице
    paginate_by = 12

    # Получаем и фильтруем список групп
    def get_queryset(self):
        queryset = super().get_queryset()
        # Поисковый запрос из URL: /groups/?q=программирование
        query = self.request.GET.get('q', '').strip()
        if query:
            # Ищем совпадение текста в названии ИЛИ описании группы (без учёта регистра)
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        return queryset

    # Передаём дополнительные данные в шаблон
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Сохраняем строку поиска для поля ввода
        context['query'] = self.request.GET.get('q', '').strip()
        # Если пользователь вошёл — передаём список групп, в которых он состоит
        if self.request.user.is_authenticated:
            context['my_groups'] = Group.objects.filter(memberships__user=self.request.user)
        return context


# ============================================================
# VIEW: GroupCreateView — Создание новой группы (/groups/create/)
# ============================================================
class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    form_class = GroupForm
    template_name = 'groups/group_create.html'

    # При успешной валидации формы
    def form_valid(self, form):
        # Назначаем создателя группы = текущий пользователь
        form.instance.creator = self.request.user
        # Сохраняем группу в БД
        response = super().form_valid(form)
        # АВТОМАТИЧЕСКИ создаём запись участника с ролью 'admin' для создателя
        GroupMembership.objects.create(group=self.object, user=self.request.user, role='admin')
        return response

    # После создания перенаправляем на страницу созданной группы
    def get_success_url(self):
        return reverse_lazy('group_detail', kwargs={'pk': self.object.pk})


# ============================================================
# VIEW: GroupDetailView — Страница группы (/groups/1/)
# Отображает шапку группы, посты группы, участников и форму публикации
# ============================================================
class GroupDetailView(DetailView):
    model = Group
    template_name = 'groups/group_detail.html'
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_object()
        user = self.request.user

        # Передаём формы для создания поста и комментария в группе
        context['post_form'] = PostForm()
        context['comment_form'] = CommentForm()

        # Получаем посты, привязанные именно к этой группе
        group_posts = (
            group.posts
            .select_related('author')
            .prefetch_related('likes', 'comments__author')
            .annotate(like_count=Count('likes'))
            .order_by('-created_at')
        )
        # Проверяем лайк пользователя для каждого поста
        if user.is_authenticated:
            for post in group_posts:
                post.is_liked = post.is_liked_by(user)

        context['posts'] = group_posts

        # Получаем всех участников этой группы
        memberships = group.memberships.select_related('user').all()
        context['memberships'] = memberships

        # Флаги статуса текущего пользователя в этой группе
        is_member = False
        user_role = None

        if user.is_authenticated:
            # Ищем запись участника для текущего пользователя
            curr = memberships.filter(user=user).first()
            if curr:
                is_member = True
                user_role = curr.role

        context['is_member'] = is_member
        context['user_role'] = user_role
        # Проверка: является ли пользователь админом/модератором группы или создателем
        context['is_group_admin'] = user_role in ['admin', 'moderator'] or group.creator == user
        return context


# ============================================================
# VIEW: GroupJoinToggleView — Вступление / Выход из группы (/groups/1/join/)
# ============================================================
class GroupJoinToggleView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        group = get_object_or_404(Group, pk=pk)
        # Проверяем, состоит ли пользователь уже в группе
        membership = GroupMembership.objects.filter(user=request.user, group=group).first()

        if membership:
            # Если состоит — выходим из группы (удаляем запись)
            # Защита: создатель группы не может так случайно выйти
            if group.creator != request.user:
                membership.delete()
        else:
            # Если не состоит — вступаем (создаём новую запись)
            GroupMembership.objects.create(
                user=request.user,
                group=group,
                role='member'
            )

        # Возвращаем пользователя на страницу этой же группы
        return redirect('group_detail', pk=group.pk)


# ============================================================
# VIEW: GroupEditView — Настройки группы (/groups/1/edit/)
# ============================================================
class GroupEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Group
    form_class = GroupForm
    template_name = 'groups/group_edit.html'

    # Проверка прав: редактировать группу может только её создатель или админ группы
    def test_func(self):
        group = self.get_object()
        user = self.request.user
        membership = group.memberships.filter(user=user).first()
        return group.creator == user or (membership and membership.role in ['admin', 'moderator']) or user.is_site_admin

    def get_success_url(self):
        return reverse_lazy('group_detail', kwargs={'pk': self.object.pk})


# ============================================================
# VIEW: GroupDeleteView — Удаление группы (/groups/1/delete/)
# ============================================================
class GroupDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Group
    success_url = reverse_lazy('group_list')

    # Проверка прав: удалить группу может только её создатель или глобальный админ сайта
    def test_func(self):
        group = self.get_object()
        user = self.request.user
        return group.creator == user or user.is_site_admin
