# ============================================================
# ФАЙЛ: apps/posts/views.py
# Описание: Обработчики для постов, комментариев и лайков
# ============================================================

# get_object_or_404 — получить объект из БД или вернуть страницу 404
# redirect — HTTP-перенаправление на другой URL
from django.shortcuts import get_object_or_404, redirect

# Базовые классы для классовых представлений:
# CreateView — страница создания объекта (форма)
# DeleteView — страница удаления объекта
# View — базовый класс (нет привязки к модели, пишем логику вручную)
from django.views.generic import CreateView, DeleteView, View

# LoginRequiredMixin — требует авторизации, иначе редирект на login
# UserPassesTestMixin — позволяет добавить проверку: "может ли пользователь это делать?"
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# reverse_lazy — строит URL по имени маршрута (лениво, для классовых views)
from django.urls import reverse_lazy

# JsonResponse — возвращает HTTP-ответ в формате JSON (для AJAX-запросов)
from django.http import JsonResponse

# Импортируем модели: пост, комментарий, лайк
from .models import Post, Comment, Like

# Импортируем формы для поста и комментария
from .forms import PostForm, CommentForm


# ============================================================
# VIEW: PostCreateView — Создание нового поста
# Обрабатывает POST-запрос с формой создания публикации
# ============================================================
class PostCreateView(LoginRequiredMixin, CreateView):

    # Модель для создания
    model = Post

    # Форма с полями content (текст) и image (фото)
    form_class = PostForm

    # URL по умолчанию — используется если нет HTTP_REFERER
    success_url = reverse_lazy('home')

    # form_valid — вызывается когда форма заполнена корректно
    def form_valid(self, form):
        # Перед сохранением в БД автоматически ставим автора поста = текущий пользователь
        # form.instance — объект Post, который будет сохранён
        form.instance.author = self.request.user
        # Вызываем родительский form_valid — он сохраняет объект в БД
        return super().form_valid(form)

    # Определяем куда перенаправить после успешного создания поста
    def get_success_url(self):
        # HTTP_REFERER — заголовок со страницей, с которой пришёл запрос
        # Если пользователь создал пост с главной — вернём его на главную
        # Если из профиля — вернём в профиль
        # Если Referer нет — fallback на главную страницу
        return self.request.META.get('HTTP_REFERER', reverse_lazy('home'))


# ============================================================
# VIEW: PostDeleteView — Удаление поста
# UserPassesTestMixin добавляет проверку прав доступа
# ============================================================
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):

    # Модель удаляемого объекта
    model = Post

    # test_func — метод из UserPassesTestMixin
    # Если возвращает False — пользователь получает HTTP 403 (Forbidden)
    def test_func(self):
        # Получаем объект поста который хотят удалить
        post = self.get_object()
        # Разрешаем удаление только автору поста ИЛИ администратору сайта
        return self.request.user == post.author or self.request.user.is_site_admin

    # После удаления — вернуться на ту же страницу (лента или профиль)
    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', reverse_lazy('home'))


# ============================================================
# VIEW: LikeToggleView — Поставить / снять лайк
# Обычный View — сами пишем обработку POST-запроса
# ============================================================
class LikeToggleView(LoginRequiredMixin, View):

    # post() — метод вызывается при HTTP POST-запросе на этот URL
    # pk — ID поста, передаётся из URL /post/<int:pk>/like/
    def post(self, request, pk):
        # Получаем пост по ID или возвращаем 404 если не существует
        post = get_object_or_404(Post, pk=pk)

        # get_or_create — ищет лайк в БД, если нет — создаёт
        # Возвращает кортеж (объект, был_создан)
        # like — объект лайка в БД
        # created — True если лайк только что создан, False если уже существовал
        like, created = Like.objects.get_or_create(post=post, user=request.user)

        # Если лайк уже существовал (created=False) — значит нажали повторно → снимаем лайк
        if not created:
            like.delete()  # Удаляем запись лайка из БД
            liked = False  # Флаг: лайка больше нет
        else:
            # Лайк только что создан — всё хорошо
            liked = True   # Флаг: лайк поставлен

        # Если запрос пришёл через AJAX (JavaScript fetch/XMLHttpRequest)
        # Проверяем специальный заголовок 'x-requested-with'
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Возвращаем JSON-ответ для JavaScript
            # {'liked': True/False, 'count': 5} — фронтенд обновляет счётчик без перезагрузки
            return JsonResponse({
                'liked': liked,
                'count': post.likes.count()
            })

        # Для обычного запроса (не AJAX) — перенаправляем обратно
        return redirect(request.META.get('HTTP_REFERER', 'home'))


# ============================================================
# VIEW: CommentCreateView — Добавить комментарий к посту
# ============================================================
class CommentCreateView(LoginRequiredMixin, CreateView):

    # Создаём объект модели Comment
    model = Comment

    # Форма с одним полем: text (текст комментария)
    form_class = CommentForm

    # form_valid вызывается при успешной валидации формы
    def form_valid(self, form):
        # Получаем пост по ID из URL /post/<int:pk>/comment/
        # self.kwargs['pk'] — значение <int:pk> из URL
        post = get_object_or_404(Post, pk=self.kwargs['pk'])

        # Привязываем комментарий к посту (поле post в модели Comment)
        form.instance.post = post

        # Привязываем комментарий к текущему авторизованному пользователю
        form.instance.author = self.request.user

        # Вызываем родительский form_valid — сохраняет комментарий в БД
        return super().form_valid(form)

    # После создания комментария — возвращаемся на ту же страницу
    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', reverse_lazy('home'))


# ============================================================
# VIEW: CommentDeleteView — Удалить комментарий
# ============================================================
class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):

    # Удаляем объект модели Comment
    model = Comment

    # Проверка прав: кто может удалить комментарий?
    def test_func(self):
        # Получаем объект комментария
        comment = self.get_object()
        # Разрешаем удаление если пользователь:
        return (
            # 1. Автор комментария — может удалить свой комментарий
            self.request.user == comment.author or
            # 2. Автор поста — может модерировать комментарии под своим постом
            self.request.user == comment.post.author or
            # 3. Администратор сайта — может удалить любой комментарий
            self.request.user.is_site_admin
        )

    # После удаления — вернуться на ту же страницу
    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', reverse_lazy('home'))
