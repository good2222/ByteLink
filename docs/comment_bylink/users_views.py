# ============================================================
# ФАЙЛ: apps/users/views.py
# Описание: Обработчики (View) для страниц пользователей
# Каждый View-класс отвечает за одну страницу сайта
# ============================================================

# render — функция для рендеринга HTML шаблона с данными
# redirect — функция для перенаправления на другой URL
from django.shortcuts import render, redirect

# reverse_lazy — строит URL по имени маршрута (как {% url %} в шаблоне)
# Используется в классовых views вместо reverse() т.к. выполняется лениво (при запросе)
from django.urls import reverse_lazy

# Базовые классы для классовых представлений:
# CreateView  — страница с формой для создания объекта
# DetailView  — страница с деталями одного объекта
# UpdateView  — страница с формой для редактирования объекта
# TemplateView — просто рендерит шаблон (без привязки к модели)
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView

# LoginRequiredMixin — миксин (примесь), который проверяет авторизацию
# Если пользователь не авторизован — перенаправляет на страницу входа
from django.contrib.auth.mixins import LoginRequiredMixin

# login — функция для авторизации пользователя (создаёт сессию)
from django.contrib.auth import login

# get_object_or_404 — получает объект из БД или возвращает HTTP 404 если не найден
from django.shortcuts import get_object_or_404

# Импортируем нашу модель пользователя
from .models import CustomUser

# Импортируем формы: для регистрации и редактирования профиля
from .forms import CustomUserCreationForm, UserProfileForm

# Импортируем модель Post чтобы показывать посты на главной и в профиле
from apps.posts.models import Post

# Импортируем формы для поста и комментария — они нужны на главной странице и в профиле
from apps.posts.forms import PostForm, CommentForm


# ============================================================
# VIEW: RegisterView — Страница регистрации (/register/)
# CreateView автоматически обрабатывает GET (показать форму) и POST (сохранить)
# ============================================================
class RegisterView(CreateView):

    # Модель, объект которой создаётся — пользователь
    model = CustomUser

    # Форма которую показываем пользователю на странице регистрации
    form_class = CustomUserCreationForm

    # HTML-шаблон для отрисовки страницы
    template_name = 'registration/register.html'

    # URL куда перенаправить после успешной регистрации
    # reverse_lazy('home') → '/' (главная страница)
    success_url = reverse_lazy('home')

    # form_valid вызывается когда форма прошла валидацию и данные корректны
    def form_valid(self, form):
        # Вызываем родительский form_valid — он сохраняет пользователя в БД
        response = super().form_valid(form)
        # self.object — только что созданный пользователь
        # login() — создаёт сессию, пользователь автоматически входит после регистрации
        login(self.request, self.object)
        # Возвращаем ответ (редирект на home)
        return response

    # dispatch вызывается самым первым, при любом типе запроса (GET или POST)
    def dispatch(self, request, *args, **kwargs):
        # Если пользователь уже авторизован — нет смысла показывать страницу регистрации
        if request.user.is_authenticated:
            # Перенаправляем его на главную
            return redirect('home')
        # Иначе продолжаем обычную обработку
        return super().dispatch(request, *args, **kwargs)


# ============================================================
# VIEW: HomeView — Главная страница / Лента (/  или /home/)
# LoginRequiredMixin — только для авторизованных пользователей
# TemplateView — просто рендерит шаблон, нет привязки к одной модели
# ============================================================
class HomeView(LoginRequiredMixin, TemplateView):

    # Шаблон главной страницы с лентой постов
    template_name = 'home.html'

    # get_context_data — подготавливает данные для шаблона
    # context — словарь переменных, доступных в шаблоне через {{ имя }}
    def get_context_data(self, **kwargs):
        # Вызываем родительский метод чтобы не потерять стандартные данные контекста
        context = super().get_context_data(**kwargs)

        # Добавляем пустую форму для создания поста (показывается в верху ленты)
        context['post_form'] = PostForm()

        # Добавляем пустую форму для написания комментария
        context['comment_form'] = CommentForm()

        # Получаем все посты из БД
        # select_related('author') — JOIN с таблицей пользователей в одном SQL-запросе
        # Без этого Django делал бы отдельный запрос для каждого поста чтобы получить автора
        # prefetch_related('likes', 'comments__author') — загружает лайки и комментарии с авторами
        # эффективно: один запрос на лайки + один на комментарии (не N запросов)
        posts = Post.objects.select_related('author').prefetch_related('likes', 'comments__author').all()

        # Для каждого поста добавляем флаг: поставил ли текущий пользователь лайк
        for post in posts:
            # is_liked_by() — метод модели Post, возвращает True/False
            # Добавляем атрибут is_liked динамически к объекту поста
            post.is_liked = post.is_liked_by(self.request.user)

        # Передаём посты в шаблон под именем 'feed_posts'
        # В шаблоне: {% for post in feed_posts %}
        context['feed_posts'] = posts

        # Возвращаем готовый словарь данных для шаблона
        return context


# ============================================================
# VIEW: ProfileView — Страница профиля пользователя (/profile/username/)
# DetailView — автоматически получает один объект из БД и передаёт в шаблон
# ============================================================
class ProfileView(LoginRequiredMixin, DetailView):

    # Модель из которой берём данные — пользователь
    model = CustomUser

    # HTML-шаблон страницы профиля
    template_name = 'users/profile.html'

    # Имя переменной в шаблоне для объекта профиля
    # В шаблоне: {{ profile_user.username }}, {{ profile_user.avatar }} и т.д.
    context_object_name = 'profile_user'

    # slug_field — поле модели по которому ищем пользователя (не по ID, а по username)
    slug_field = 'username'

    # slug_url_kwarg — название параметра в URL: /profile/<str:username>/
    slug_url_kwarg = 'username'

    # Добавляем дополнительные данные в контекст шаблона
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Форма для создания поста (если смотрим свой профиль)
        context['post_form'] = PostForm()

        # Форма для комментария
        context['comment_form'] = CommentForm()

        # self.object — объект пользователя, чей профиль просматривается
        # .posts — все посты этого пользователя (through related_name='posts')
        posts = self.object.posts.select_related('author').prefetch_related('likes', 'comments__author').all()

        # Помечаем, поставил ли текущий пользователь лайк каждому посту
        for post in posts:
            post.is_liked = post.is_liked_by(self.request.user)

        # Передаём посты пользователя в шаблон
        context['user_posts'] = posts

        # Флаг: просматривает ли пользователь свой собственный профиль
        # Если True — показываем кнопку "Редактировать" вместо "Добавить в друзья"
        context['is_own_profile'] = self.object == self.request.user

        return context


# ============================================================
# VIEW: ProfileEditView — Страница редактирования профиля (/profile/edit/)
# UpdateView — показывает форму с текущими данными, сохраняет изменения
# ============================================================
class ProfileEditView(LoginRequiredMixin, UpdateView):

    # Модель для обновления — пользователь
    model = CustomUser

    # Форма с полями: имя, фамилия, bio, статус, аватар, обложка, дата рождения, город, сайт
    form_class = UserProfileForm

    # HTML-шаблон страницы редактирования
    template_name = 'users/profile_edit.html'

    # get_object — определяет КАКОЙ объект редактируем
    # По умолчанию UpdateView ищет объект по pk в URL, но нам нужен текущий пользователь
    def get_object(self, queryset=None):
        # Возвращаем текущего авторизованного пользователя
        # Это гарантирует что пользователь редактирует только свой профиль
        return self.request.user

    # URL для перенаправления после успешного сохранения
    def get_success_url(self):
        # Перенаправляем обратно на профиль пользователя
        # kwargs={'username': ...} — передаём username в URL /profile/egor/
        return reverse_lazy('profile', kwargs={'username': self.request.user.username})
