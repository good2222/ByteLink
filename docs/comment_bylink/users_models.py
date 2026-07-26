# =====================================================================
# ФАЙЛ: apps/users/models.py
# ЧТО ДЕЛАЕТ ЭТОТ ФАЙЛ:
#   Описывает структуру таблиц в базе данных для раздела "Пользователи".
#   Здесь 2 модели:
#   1. CustomUser  — расширенная модель пользователя (аватар, роль, друзья и т.д.)
#   2. FriendRequest — заявка в друзья от одного пользователя к другому.
# =====================================================================

from django.db import models
# models — библиотека Django для описания таблиц в базе данных.
# Каждый класс с models.Model = одна таблица в БД.

from django.contrib.auth.models import AbstractUser
# AbstractUser — уже готовая модель пользователя от Django.
# Содержит поля: username, password, email, first_name, last_name, is_active...
# Мы НАСЛЕДУЕМСЯ от неё, чтобы добавить свои поля (аватар, статус, роль).
# Наследование = "взять всё что есть и добавить своё".


# =====================================================================
# КЛАСС CustomUser — Наш пользователь сайта ByteLink
# =====================================================================
class CustomUser(AbstractUser):
    # CustomUser наследует ВСЕ поля AbstractUser + добавляет свои.
    # В базе данных это одна таблица "users_customuser".

    # ROLE_CHOICES — список допустимых значений для поля role.
    # Формат: (значение_в_БД, читаемое_название).
    ROLE_CHOICES = (
        ('user', 'Пользователь'),
        # 'user' — то что хранится в БД. 'Пользователь' — то что видит человек.
        ('admin', 'Администратор'),
        # 'admin' — администратор сайта, имеет расширенные права.
    )

    role = models.CharField(
        # CharField — строковое поле фиксированной длины (текст).
        max_length=10,
        # max_length=10 — максимум 10 символов (слово 'admin' = 5 символов, влезает).
        choices=ROLE_CHOICES,
        # choices — Django покажет выпадающий список в форме, только эти 2 варианта.
        default='user',
        # default='user' — если не указать роль, автоматически ставится 'user'.
        verbose_name='Роль'
        # verbose_name — красивое название поля в панели администратора Django Admin.
    )

    bio = models.TextField(
        # TextField — строка без ограничения длины (для длинных текстов).
        max_length=500,
        # max_length=500 — максимум 500 символов для "О себе".
        blank=True,
        # blank=True — поле НЕ ОБЯЗАТЕЛЬНО для заполнения в форме.
        verbose_name='О себе'
    )

    status_message = models.CharField(
        max_length=150,
        blank=True,
        # blank=True — статус можно не заполнять, поле останется пустым.
        verbose_name='Статус'
        # Например: "Изучаю Django" или "В сети".
    )

    avatar = models.ImageField(
        # ImageField — поле для загрузки изображения (требует библиотеку Pillow).
        upload_to='avatars/',
        # upload_to='avatars/' — загруженные файлы сохранятся в папке media/avatars/
        default='avatars/default.png',
        # default — если пользователь не загрузил аватар, использовать этот файл.
        blank=True,
        verbose_name='Аватар'
    )

    cover_image = models.ImageField(
        upload_to='covers/',
        # covers/ — обложки профиля хранятся в media/covers/
        default='covers/default.png',
        blank=True,
        verbose_name='Обложка профиля'
        # Как в ВКонтакте — большое фото вверху страницы профиля.
    )

    birth_date = models.DateField(
        # DateField — поле для даты (год-месяц-день, без времени).
        null=True,
        # null=True — в базе данных разрешено хранить NULL (пустое значение).
        blank=True,
        # blank=True — поле не обязательно в форме.
        # ВАЖНО: для необязательных дат нужно ОБА: null=True и blank=True.
        verbose_name='Дата рождения'
    )

    location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Местоположение'
        # Например: "Киев, Украина"
    )

    website = models.URLField(
        # URLField — специальное поле для ссылок. Django автоматически
        # проверит что введённое значение похоже на URL (начинается с http://).
        max_length=200,
        blank=True,
        verbose_name='Сайт'
    )

    class Meta:
        # Meta — внутренний класс с настройками модели (не поля, а поведение).
        verbose_name = 'Пользователь'
        # verbose_name — единственное число в Django Admin: "Пользователь".
        verbose_name_plural = 'Пользователи'
        # verbose_name_plural — множественное число в Django Admin: "Пользователи".

    @property
    def is_site_admin(self):
        # @property — декоратор, превращает метод в "умное поле".
        # Вызывается как атрибут: user.is_site_admin (без скобок).
        # Возвращает True если пользователь — администратор сайта.
        return self.role == 'admin' or self.is_superuser
        # self.role == 'admin' — проверяем поле role.
        # self.is_superuser — стандартное поле Django (суперпользователь из AbstractUser).
        # or — если хотя бы одно из условий верно — возвращаем True.

    @property
    def get_avatar_url(self):
        # Возвращает URL аватара. Если файл не найден — возвращает URL заглушки.
        # Это защита: если файл удалили с диска, сайт не сломается с ошибкой 404.
        if self.avatar and hasattr(self.avatar, 'url'):
            # hasattr(self.avatar, 'url') — проверяем что у объекта есть атрибут url.
            try:
                if self.avatar.storage.exists(self.avatar.name):
                    # self.avatar.storage.exists() — проверяем что файл реально есть на диске.
                    return self.avatar.url
                    # .url — полный URL файла, например /media/avatars/photo.jpg
            except Exception:
                # Exception — перехватываем любую ошибку (файл недоступен, диск сломан и т.д.)
                pass
                # pass — ничего не делаем, просто идём дальше к заглушке.
        from django.templatetags.static import static
        # static() — функция для получения URL статических файлов (CSS, JS, картинки).
        return static('images/default-avatar.png')
        # Возвращаем URL картинки-заглушки из папки static/images/

    @property
    def get_cover_url(self):
        # Аналогично get_avatar_url, но для обложки профиля.
        if self.cover_image and hasattr(self.cover_image, 'url'):
            try:
                if self.cover_image.storage.exists(self.cover_image.name):
                    return self.cover_image.url
            except Exception:
                pass
        from django.templatetags.static import static
        return static('images/default-cover.png')

    def get_friends(self):
        """Возвращает QuerySet всех подтверждённых друзей пользователя."""
        # Находим все принятые заявки в друзья где участвует ЭТОТ пользователь.
        # Q() — специальный объект для сложных условий WHERE в SQL.
        # models.Q(from_user=self) | models.Q(to_user=self)
        # = WHERE from_user=я ИЛИ to_user=я
        accepted = FriendRequest.objects.filter(
            models.Q(from_user=self) | models.Q(to_user=self),
            # запятая = И (AND в SQL). Итого: (from=я ИЛИ to=я) И статус=принята.
            status='accepted'
        )

        friend_ids = []
        # Собираем ID всех друзей в список.
        for req in accepted:
            # Для каждой заявки: если Я отправитель — друг это получатель, и наоборот.
            friend_ids.append(req.to_user_id if req.from_user_id == self.pk else req.from_user_id)
            # req.from_user_id — ID поля ForeignKey без лишнего SQL-запроса (быстрее чем req.from_user.id).

        return CustomUser.objects.filter(pk__in=friend_ids)
        # pk__in=friend_ids — WHERE id IN (список_id) — выбирает всех пользователей из списка.

    def get_pending_received_count(self):
        """Количество входящих заявок в друзья (для красного бейджа в навбаре)."""
        return FriendRequest.objects.filter(to_user=self, status='pending').count()
        # .count() — SQL запрос COUNT(*) — возвращает число, а не список объектов.
        # Быстрее чем .all() а потом len().

    def __str__(self):
        # __str__ — "магический метод". Вызывается когда объект нужно
        # преобразовать в строку. Например в Django Admin или в print().
        return self.username


# =====================================================================
# КЛАСС FriendRequest — Заявка в друзья
# Аналог кнопки "Добавить в друзья" в ВКонтакте.
# Хранит: кто отправил, кому, и каков статус заявки.
# =====================================================================
class FriendRequest(models.Model):

    STATUS_CHOICES = (
        ('pending',  'Ожидает'),
        # 'pending' — заявка отправлена, но ещё не принята и не отклонена.
        ('accepted', 'Принята'),
        # 'accepted' — получатель нажал "Принять". Теперь они друзья.
        ('declined', 'Отклонена'),
        # 'declined' — получатель нажал "Отклонить".
    )

    from_user = models.ForeignKey(
        CustomUser,
        # ForeignKey — связь "многие к одному". Один пользователь может
        # отправить много заявок разным людям.
        on_delete=models.CASCADE,
        # CASCADE — если пользователь удалён, все его заявки тоже удаляются.
        related_name='sent_requests',
        # related_name='sent_requests' — обратная связь.
        # Позволяет писать: user.sent_requests.all() — все исходящие заявки.
        verbose_name='Отправитель'
    )
    to_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='received_requests',
        # user.received_requests.all() — все входящие заявки.
        verbose_name='Получатель'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        # Новая заявка по умолчанию имеет статус 'pending' (ожидает ответа).
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    # auto_now_add=True — Django АВТОМАТИЧЕСКИ записывает текущее время
    # в момент создания записи. Изменить вручную нельзя.

    class Meta:
        unique_together = ('from_user', 'to_user')
        # unique_together — запрещает дублирование. Один пользователь не может
        # отправить другому ДВЕ заявки одновременно. Защита на уровне БД.
        verbose_name = 'Заявка в друзья'
        verbose_name_plural = 'Заявки в друзья'

    def __str__(self):
        return f'{self.from_user} → {self.to_user} [{self.status}]'
        # f-строка — строка с подстановкой переменных.
        # Пример: "alice → bob [pending]"
