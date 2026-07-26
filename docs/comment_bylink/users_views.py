# =====================================================================
# ФАЙЛ: apps/users/views.py
# ЧТО ДЕЛАЕТ ЭТОТ ФАЙЛ:
#   Views (Представления) — это функции/классы которые обрабатывают
#   HTTP-запросы пользователя и возвращают HTML-страницу в ответ.
#
#   Схема: Браузер → URL → View → (читает/пишет в БД) → Template → HTML
#
#   В этом файле views для:
#   - Регистрации нового пользователя
#   - Главной страницы (лента постов)
#   - Страницы профиля
#   - Редактирования профиля
#   - Поиска пользователей
#   - Системы друзей (список, заявки, принять/отклонить/удалить)
# =====================================================================

from django.shortcuts import render, redirect, get_object_or_404
# render(request, template, context) — рендерит HTML-шаблон и возвращает HTTP-ответ.
# redirect(url_name) — перенаправляет браузер на другую страницу (HTTP 302).
# get_object_or_404(Model, **kwargs) — ищет объект в БД. Если не нашёл — отдаёт 404.

from django.urls import reverse_lazy
# reverse_lazy('url_name') — преобразует имя URL-маршрута в адрес '/profile/'.
# lazy (ленивый) — вычисляется только когда реально нужен (важно при инициализации класса).

from django.views.generic import CreateView, DetailView, UpdateView, TemplateView, View, ListView
# Django предоставляет готовые "классовые представления" (Class-Based Views, CBV):
# CreateView  — для создания объекта (показывает форму, сохраняет в БД).
# DetailView  — для показа одного объекта по ID или slug.
# UpdateView  — для редактирования существующего объекта.
# TemplateView — просто рендерит шаблон (без модели).
# View        — самый базовый класс. Методы get() и post() пишешь сам.
# ListView    — для показа списка объектов.

from django.contrib.auth.mixins import LoginRequiredMixin
# LoginRequiredMixin — "примесь" (mixin). Добавь её в класс View,
# и Django автоматически проверит: вошёл ли пользователь?
# Если НЕТ — перенаправит на страницу входа (settings.LOGIN_URL).

from django.contrib.auth import login
# login(request, user) — создаёт сессию. После этого request.user = вошедший пользователь.

from django.db.models import Count, Q
# Count — функция агрегации SQL: COUNT(*). Считает количество связанных объектов.
# Q — объект для сложных SQL условий: Q(a=1) | Q(b=2) = WHERE a=1 OR b=2.

from django.contrib import messages
# messages — фреймворк Django для одноразовых сообщений.
# messages.success(request, 'Текст') — добавляет сообщение в сессию.
# В шаблоне {{ messages }} показывает его один раз, потом удаляет.

from .models import CustomUser, FriendRequest
# . (точка) = текущий пакет (apps/users/). Импортируем наши модели.

from .forms import CustomUserCreationForm, UserProfileForm
# Формы — классы Django для HTML-форм. Описывают поля, валидацию, отображение.

from apps.posts.models import Post
# Импортируем модель Post из другого приложения для отображения постов в ленте.

from apps.posts.forms import PostForm, CommentForm
# PostForm, CommentForm — формы для создания постов и комментариев прямо с ленты.


# =====================================================================
# RegisterView — Страница регистрации нового пользователя
# URL: /register/
# =====================================================================
class RegisterView(CreateView):
    # CreateView — готовый класс для создания объекта через форму.
    # Автоматически: показывает форму (GET) + сохраняет объект в БД (POST).

    model = CustomUser
    # model — с какой моделью работаем. CreateView создаст объект CustomUser.

    form_class = CustomUserCreationForm
    # form_class — какую форму показывать пользователю для заполнения.

    template_name = 'registration/register.html'
    # template_name — путь к HTML-шаблону который будет отображаться.

    success_url = reverse_lazy('home')
    # success_url — куда перенаправить ПОСЛЕ успешного создания.
    # reverse_lazy('home') = '/'. Перейдёт на главную.

    def form_valid(self, form):
        # form_valid() — вызывается когда форма прошла валидацию (все поля верны).
        # Переопределяем чтобы СРАЗУ входить в систему после регистрации.
        response = super().form_valid(form)
        # super().form_valid(form) — вызываем оригинальный метод CreateView,
        # который сохраняет пользователя в БД. self.object = созданный пользователь.
        login(self.request, self.object)
        # login() — создаём сессию. Пользователь сразу входит на сайт.
        # Без этого после регистрации нужно было бы входить отдельно.
        return response

    def dispatch(self, request, *args, **kwargs):
        # dispatch() — первый метод который вызывается при любом запросе.
        # Переопределяем чтобы уже вошедших пользователей не пускать на /register/.
        if request.user.is_authenticated:
            # is_authenticated — True если пользователь вошёл в систему.
            return redirect('home')
            # Уже зарегистрирован? Перенаправляем на главную.
        return super().dispatch(request, *args, **kwargs)
        # Если НЕ авторизован — продолжаем стандартную обработку.


# =====================================================================
# HomeView — Главная страница / Лента новостей
# URL: / (корень сайта)
# =====================================================================
class HomeView(LoginRequiredMixin, TemplateView):
    # LoginRequiredMixin — первым делом проверяет авторизацию.
    # Если не вошёл — перенаправит на /login/.
    # TemplateView — просто рендерит шаблон, БЕЗ автоматической модели.

    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        # get_context_data() — метод для передачи данных в шаблон.
        # **kwargs — принимает любые именованные аргументы (стандарт Django CBV).
        context = super().get_context_data(**kwargs)
        # Вызываем родительский метод чтобы получить базовый context-словарь.

        context['post_form'] = PostForm()
        # Добавляем пустую форму поста — она рендерится прямо на главной странице.

        context['comment_form'] = CommentForm()
        # Пустая форма комментария (для каждого поста).

        friends = self.request.user.get_friends()
        # get_friends() — наш метод из models.py. Возвращает всех друзей текущего юзера.

        # Формируем умную ленту постов:
        posts = (
            Post.objects
            # Post.objects — менеджер запросов Django (как посредник между кодом и SQL).

            .select_related('author')
            # select_related('author') — ОПТИМИЗАЦИЯ: делает SQL JOIN с таблицей автора.
            # Без него: для каждого поста из 100 — отдельный SQL-запрос к юзерам (100 запросов!).
            # С ним: всё в одном запросе. Это решение проблемы "N+1 запросов".

            .prefetch_related('likes', 'comments__author')
            # prefetch_related — другой тип оптимизации для ManyToMany и обратных FK.
            # 'likes' — все лайки постов загружаются одним дополнительным запросом.
            # 'comments__author' — комментарии + их авторы загружаются 2-мя запросами.
            # __ (двойное подчёркивание) — переход по связи в ORM Django.

            .filter(Q(author=self.request.user) | Q(author__in=friends))
            # filter() — WHERE в SQL. Показываем посты:
            # Q(author=self.request.user) — мои собственные посты, ИЛИ
            # Q(author__in=friends) — посты моих друзей.
            # author__in — WHERE author_id IN (список id друзей).

            .annotate(like_count=Count('likes'))
            # annotate() — добавляет вычисляемое поле к каждому посту.
            # like_count=Count('likes') — считает количество лайков КАЖДОГО поста.
            # Это делается в ОДНОМ SQL запросе с GROUP BY. Очень эффективно!

            .order_by('-like_count', '-created_at')
            # order_by() — сортировка. ORDER BY в SQL.
            # '-like_count' — минус = DESC (убывающий порядок). Больше лайков = выше.
            # '-created_at' — если лайков поровну — новее посты идут первыми.
        )

        for post in posts:
            # Для каждого поста добавляем атрибут: лайкнул ли текущий юзер этот пост.
            post.is_liked = post.is_liked_by(self.request.user)
            # is_liked_by() — метод из Post модели (проверяет наличие Like в БД).
            # Нам нужно это чтобы в шаблоне показать "сердечко" закрашенным или нет.

        context['feed_posts'] = posts
        # Передаём посты в шаблон под ключом 'feed_posts'.
        # В шаблоне: {% for post in feed_posts %}

        return context


# =====================================================================
# ProfileView — Страница профиля пользователя
# URL: /profile/<username>/
# =====================================================================
class ProfileView(LoginRequiredMixin, DetailView):
    # DetailView — готовый класс для показа ОДНОГО объекта.

    model = CustomUser
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'
    # context_object_name — под каким именем объект передаётся в шаблон.
    # Без этого Django передаёт под именем 'object' или 'customuser'. С этим — 'profile_user'.

    slug_field = 'username'
    # slug_field — какое поле модели считать "slug" (уникальный текстовый идентификатор).
    # Django будет искать пользователя по полю username, а не по pk (id).

    slug_url_kwarg = 'username'
    # slug_url_kwarg — имя параметра в URL: path('profile/<str:username>/', ...)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # self.object — объект пользователя которого просматриваем (установлен DetailView).

        context['post_form'] = PostForm()
        context['comment_form'] = CommentForm()

        # Посты этого пользователя, сортировка по лайкам:
        posts = (
            self.object.posts       # self.object.posts — все посты этого юзера.
            # .posts работает благодаря related_name='posts' в модели Post.
            .select_related('author')
            .prefetch_related('likes', 'comments__author')
            .annotate(like_count=Count('likes'))
            .order_by('-like_count', '-created_at')
        )
        for post in posts:
            post.is_liked = post.is_liked_by(self.request.user)
        context['user_posts'] = posts

        context['is_own_profile'] = self.object == self.request.user
        # True если я смотрю свой профиль (показываем кнопку "Редактировать").
        # False если это профиль другого юзера (показываем кнопку "Добавить в друзья").

        context['friends'] = self.object.get_friends()[:6]
        # [:6] — срез Python: берём только первые 6 друзей для блока "Друзья" в профиле.

        context['friends_count'] = self.object.get_friends().count()
        # Общее количество друзей для отображения числа.

        if not context['is_own_profile']:
            # Если смотрим чужой профиль — определяем статус дружбы.
            me = self.request.user
            other = self.object
            req = FriendRequest.objects.filter(
                Q(from_user=me, to_user=other) | Q(from_user=other, to_user=me)
            ).first()
            # .first() — берём первый (или None если нет ни одного).
            # Ищем любую заявку между нами двумя, в любую сторону.

            context['friend_request'] = req
            # Передаём объект заявки в шаблон.

            if req:
                context['are_friends'] = req.status == 'accepted'
                # True = мы уже друзья. Показываем кнопку "Удалить из друзей".

                context['request_pending_sent'] = req.status == 'pending' and req.from_user == me
                # True = я отправил заявку, она ещё ожидает. Показываем "Заявка отправлена".

                context['request_pending_received'] = req.status == 'pending' and req.to_user == me
                # True = он отправил мне заявку. Показываем кнопки "Принять" / "Отклонить".
            else:
                # Заявки нет вообще. Показываем кнопку "Добавить в друзья".
                context['are_friends'] = False
                context['request_pending_sent'] = False
                context['request_pending_received'] = False

        return context


# =====================================================================
# ProfileEditView — Редактирование профиля текущего пользователя
# URL: /profile/edit/
# =====================================================================
class ProfileEditView(LoginRequiredMixin, UpdateView):
    # UpdateView — готовый класс для редактирования объекта через форму.

    model = CustomUser
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'

    def get_object(self, queryset=None):
        # get_object() — переопределяем чтобы редактировать ТОЛЬКО СВОЙ профиль.
        # По умолчанию UpdateView ищет объект по pk из URL.
        # Мы заменяем это: всегда редактируем текущего пользователя.
        return self.request.user
        # request.user — пользователь из текущей сессии (тот кто вошёл в систему).

    def get_success_url(self):
        # После успешного сохранения — перенаправляем на страницу профиля.
        return reverse_lazy('profile', kwargs={'username': self.request.user.username})
        # kwargs={'username': ...} — передаём аргумент в URL-шаблон /profile/<username>/


# =====================================================================
# UserSearchView — Поиск пользователей
# URL: /users/search/?q=запрос
# =====================================================================
class UserSearchView(LoginRequiredMixin, ListView):
    # ListView — показывает список объектов. Автоматически передаёт в шаблон queryset.

    template_name = 'users/search.html'
    context_object_name = 'results'
    # context_object_name — в шаблоне: {% for user in results %}

    paginate_by = 20
    # paginate_by — ListView автоматически нарежет результаты по 20 на страницу.
    # В шаблоне: page_obj, paginator, is_paginated для кнопок "Следующая/Предыдущая".

    def get_queryset(self):
        # get_queryset() — метод который возвращает список объектов для показа.

        query = self.request.GET.get('q', '').strip()
        # request.GET — словарь GET-параметров из URL.
        # .get('q', '') — берём параметр 'q', если нет — пустая строка.
        # .strip() — убираем пробелы по краям.

        if not query:
            return CustomUser.objects.none()
            # objects.none() — пустой QuerySet. Ничего не показываем если запрос пустой.

        return (
            CustomUser.objects
            .filter(
                Q(username__icontains=query) |
                # __icontains — SQL ILIKE '%query%'. Поиск без учёта регистра.
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
                # Ищем по имени, фамилии или юзернейму.
            )
            .exclude(pk=self.request.user.pk)
            # .exclude() — исключаем из результатов. Себя в поиске не показываем.
            .order_by('username')
            # Сортируем по алфавиту.
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        # Передаём поисковый запрос чтобы он остался в поле input в шаблоне.
        return context


# =====================================================================
# FriendsListView — Список друзей пользователя
# URL: /friends/ или /friends/<username>/
# =====================================================================
class FriendsListView(LoginRequiredMixin, View):
    # View — базовый класс. Мы сами пишем метод get() для обработки GET-запросов.

    def get(self, request, username=None):
        # username=None — параметр необязательный.
        # Если передан username — показываем друзей другого юзера.
        # Если не передан — показываем своих друзей.

        if username:
            profile_user = get_object_or_404(CustomUser, username=username)
            # get_object_or_404 — если пользователь не найден — возвращает страницу 404.
        else:
            profile_user = request.user
            # Без username — показываем свои собственные друзья.

        friends = profile_user.get_friends()
        # get_friends() — метод из CustomUser, возвращает всех принятых друзей.

        return render(request, 'users/friends.html', {
            # render() — рендерит шаблон friends.html с этими данными.
            'profile_user': profile_user,
            'friends': friends,
        })


# =====================================================================
# FriendRequestsView — Входящие заявки в друзья
# URL: /friend-requests/
# =====================================================================
class FriendRequestsView(LoginRequiredMixin, View):
    def get(self, request):
        incoming = FriendRequest.objects.filter(
            to_user=request.user,   # адресованные текущему пользователю
            status='pending'         # только ожидающие (не принятые/отклонённые)
        ).select_related('from_user').order_by('-created_at')
        # select_related('from_user') — загружаем отправителя одним JOIN-запросом.
        # order_by('-created_at') — сначала самые новые заявки.

        return render(request, 'users/friend_requests.html', {
            'incoming': incoming,
        })


# =====================================================================
# SendFriendRequestView — Отправить заявку в друзья
# URL: /friends/request/send/<username>/  (POST-запрос)
# =====================================================================
class SendFriendRequestView(LoginRequiredMixin, View):
    def post(self, request, username):
        # Метод post() обрабатывает POST-запросы (отправка формы, клик кнопки).

        to_user = get_object_or_404(CustomUser, username=username)
        # Находим пользователя которому отправляем заявку.

        if to_user == request.user:
            # Защита: нельзя добавить самого себя в друзья.
            messages.error(request, 'Нельзя добавить себя в друзья.')
            return redirect('profile', username=username)

        existing = FriendRequest.objects.filter(
            Q(from_user=request.user, to_user=to_user) |
            Q(from_user=to_user, to_user=request.user)
        ).first()
        # Ищем заявку в любую сторону — а вдруг он уже отправил заявку мне?

        if existing:
            # Заявка уже есть. Возможно отклонённая.
            if existing.status == 'declined' and existing.from_user == request.user:
                # Если Я отправлял и мне отклонили — можно отправить снова.
                existing.status = 'pending'
                existing.save()
                # .save() — сохраняем изменённый объект в БД. SQL: UPDATE.
                messages.success(request, f'Заявка отправлена пользователю {to_user.username}.')
            else:
                messages.info(request, 'Заявка уже существует.')
        else:
            # Заявки не было — создаём новую.
            FriendRequest.objects.create(from_user=request.user, to_user=to_user)
            # .create() — SQL INSERT. Создаёт запись в таблице friend_requests.
            messages.success(request, f'Заявка отправлена пользователю {to_user.username}.')

        return redirect('profile', username=username)
        # После отправки — возвращаем на профиль этого пользователя.


# =====================================================================
# AcceptFriendRequestView — Принять заявку в друзья
# URL: /friends/request/<pk>/accept/  (POST-запрос)
# =====================================================================
class AcceptFriendRequestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        # pk — первичный ключ (ID) заявки в БД.
        freq = get_object_or_404(FriendRequest, pk=pk, to_user=request.user, status='pending')
        # get_object_or_404 с несколькими аргументами — это защита!
        # Мы не просто ищем по pk. Мы требуем:
        # - to_user=request.user — эта заявка адресована МНЕ (нельзя принять чужую).
        # - status='pending' — она ещё ожидает (нельзя принять уже принятую).
        freq.status = 'accepted'
        # Меняем статус с 'pending' на 'accepted'.
        freq.save()
        # SQL: UPDATE friend_requests SET status='accepted' WHERE id=pk
        messages.success(request, f'Вы приняли заявку от {freq.from_user.username}.')
        return redirect(request.META.get('HTTP_REFERER', 'friend_requests'))
        # HTTP_REFERER — заголовок браузера с URL предыдущей страницы.
        # Возвращаемся туда откуда пришли. Если нет — на страницу заявок.


# =====================================================================
# DeclineFriendRequestView — Отклонить заявку в друзья
# =====================================================================
class DeclineFriendRequestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        freq = get_object_or_404(FriendRequest, pk=pk, to_user=request.user, status='pending')
        freq.status = 'declined'
        freq.save()
        messages.info(request, f'Заявка от {freq.from_user.username} отклонена.')
        return redirect(request.META.get('HTTP_REFERER', 'friend_requests'))


# =====================================================================
# RemoveFriendView — Удалить из друзей
# URL: /friends/remove/<username>/  (POST-запрос)
# =====================================================================
class RemoveFriendView(LoginRequiredMixin, View):
    def post(self, request, username):
        other = get_object_or_404(CustomUser, username=username)
        FriendRequest.objects.filter(
            Q(from_user=request.user, to_user=other) |
            Q(from_user=other, to_user=request.user)
        ).delete()
        # .delete() — SQL DELETE. Удаляем заявку/дружбу полностью из БД.
        # Ищем в обе стороны на случай кто кому первым отправлял.
        messages.success(request, f'{other.username} удалён из друзей.')
        return redirect('profile', username=username)
