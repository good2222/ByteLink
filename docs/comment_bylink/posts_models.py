# =====================================================================
# ФАЙЛ: apps/posts/models.py
# ЧТО ДЕЛАЕТ ЭТОТ ФАЙЛ:
#   Описывает 3 таблицы в базе данных:
#   1. Post    — публикации пользователей (текст, фото)
#   2. Comment — комментарии к постам
#   3. Like    — лайки (кто поставил лайк какому посту)
# =====================================================================

from django.db import models
# models — основной модуль для описания структуры таблиц в БД.

from django.conf import settings
# settings — настройки проекта (settings.py).
# settings.AUTH_USER_MODEL — строка 'users.CustomUser'.
# Используем так, а не импортируем CustomUser напрямую,
# чтобы избежать кольцевых импортов между приложениями.

from django.db.models import Count
# Count — функция агрегации. Используется в запросах annotate(like_count=Count('likes')).


# =====================================================================
# КЛАСС Post — Одна публикация в социальной сети
# Аналог поста в ВКонтакте / записи в Facebook.
# =====================================================================
class Post(models.Model):

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        # ForeignKey — связь "многие к одному". Один пользователь → много постов.
        on_delete=models.CASCADE,
        # CASCADE — если удалить пользователя, все его посты тоже удалятся.
        related_name='posts'
        # related_name='posts' — обратная связь. Теперь можно писать:
        # user.posts.all() — все посты этого пользователя.
    )

    content = models.TextField(verbose_name='Текст публикации')
    # TextField — поле для длинного текста (без ограничения длины).
    # verbose_name — имя поля в Django Admin панели.

    image = models.ImageField(
        upload_to='posts_images/',
        # upload_to — папка для сохранения: media/posts_images/
        blank=True,
        # blank=True — изображение необязательно. Пост может быть только с текстом.
        null=True,
        # null=True — в БД разрешено хранить NULL (пустое значение) для этого поля.
        # Для FileField/ImageField нужно ОБА: null=True и blank=True.
        verbose_name='Изображение'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    # auto_now_add=True — время создания. Django ставит АВТОМАТИЧЕСКИ, изменить нельзя.
    # Тип: datetime (дата + время + секунды).

    updated_at = models.DateTimeField(auto_now=True)
    # auto_now=True — время ПОСЛЕДНЕГО ИЗМЕНЕНИЯ. Обновляется при каждом .save().
    # Разница: auto_now_add — только при создании. auto_now — при каждом сохранении.

    group = models.ForeignKey(
        "groups.Group",
        # "groups.Group" — строка вместо импорта класса. Django найдёт модель сам.
        # Используем строку чтобы избежать кольцевого импорта (Post и Group ссылаются друг на друга).
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        # null=True, blank=True — пост может быть без группы (обычный пост в ленте).
        related_name='posts',
        # group.posts.all() — все посты этой группы.
        verbose_name='Группа'
    )

    class Meta:
        ordering = ['-created_at']
        # ordering — сортировка по умолчанию для всех запросов Post.objects.all().
        # '-created_at' — минус = DESC = сначала новые посты.
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return f'Пост #{self.id} от {self.author.username}'
        # Например: "Пост #42 от alice". Отображается в Django Admin и при print().

    @property
    def likes_count(self):
        # @property — метод работает как атрибут: post.likes_count (без скобок).
        return self.likes.count()
        # self.likes — обратная связь к модели Like (related_name='likes').
        # .count() — SQL: SELECT COUNT(*) FROM likes WHERE post_id=42.

    @property
    def comments_count(self):
        return self.comments.count()
        # Аналогично — количество комментариев к этому посту.

    def is_liked_by(self, user):
        # Метод принимает объект пользователя и возвращает True/False.
        # Используется в views: post.is_liked = post.is_liked_by(request.user)
        if not user.is_authenticated:
            # Анонимный пользователь не может лайкать.
            return False
        return self.likes.filter(user=user).exists()
        # .exists() — SQL: SELECT EXISTS (SELECT 1 FROM likes WHERE post_id=X AND user_id=Y)
        # Быстрее чем .count() > 0, потому что останавливается при нахождении первой записи.


# =====================================================================
# КЛАСС Comment — Комментарий к посту
# =====================================================================
class Comment(models.Model):

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        # Удалили пост — удалились все его комментарии.
        related_name='comments'
        # post.comments.all() — все комментарии к этому посту.
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
        # user.comments.all() — все комментарии этого пользователя.
    )
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        # Комментарии сортируются от старых к новым (хронологический порядок).
        # Нет минуса — ASC (возрастающий порядок).
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'Комментарий {self.author.username} к посту #{self.post.id}'


# =====================================================================
# КЛАСС Like — Лайк (отметка "Нравится")
# =====================================================================
class Like(models.Model):

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes'
        # post.likes.all() — все лайки этого поста.
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes'
        # user.likes.all() — все лайки которые поставил этот пользователь.
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
        # unique_together — ограничение на уровне БД:
        # Одна пара (post, user) может быть только ОДИН РАЗ.
        # Это значит: пользователь не может поставить лайк дважды одному посту.
        # SQL: UNIQUE KEY (post_id, user_id)
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'

    def __str__(self):
        return f'Лайк {self.user.username} на пост #{self.post.id}'
