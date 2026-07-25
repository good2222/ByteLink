# ============================================================
# ФАЙЛ: apps/posts/models.py
# Описание: Модели Публикации, Комментария и Лайка
# ============================================================

# Импортируем модуль models — содержит все типы полей для таблиц базы данных
from django.db import models

# settings — объект настроек Django, используем его чтобы получить AUTH_USER_MODEL
# Это лучше, чем напрямую импортировать CustomUser, т.к. избегает циклических импортов
from django.conf import settings


# ============================================================
# МОДЕЛЬ: Post (Публикация)
# Каждый объект Post = одна строка в таблице posts в базе данных
# ============================================================
class Post(models.Model):

    # Автор поста — внешний ключ (ForeignKey) на модель пользователя
    # settings.AUTH_USER_MODEL = 'users.CustomUser' (задан в settings.py)
    # on_delete=models.CASCADE — если пользователь удаляется, все его посты тоже удаляются
    # related_name='posts' — позволяет обратиться к постам пользователя: user.posts.all()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')

    # Текстовое содержимое поста — без ограничения длины (TextField)
    # verbose_name — название поля в Django Admin
    content = models.TextField(verbose_name='Текст публикации')

    # Прикреплённое изображение к посту (необязательное)
    # upload_to='posts_images/' — файлы сохраняются в папку media/posts_images/
    # blank=True — форма не требует обязательного заполнения
    # null=True — в базе данных разрешено хранить NULL (поле пустое)
    image = models.ImageField(upload_to='posts_images/', blank=True, null=True, verbose_name='Изображение')

    # Дата и время создания поста
    # auto_now_add=True — Django автоматически ставит текущее время при создании объекта
    # Это поле нельзя изменить вручную
    created_at = models.DateTimeField(auto_now_add=True)

    # Дата и время последнего изменения поста
    # auto_now=True — Django автоматически обновляет время при каждом сохранении объекта
    updated_at = models.DateTimeField(auto_now=True)

    # Мета-настройки модели
    class Meta:
        # Сортировка по умолчанию: '-created_at' — минус означает сортировку по убыванию
        # Самые свежие посты будут первыми в списке
        ordering = ['-created_at']
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'

    # Строковое представление объекта для Django Admin и логов
    def __str__(self):
        # Пример: "Пост #3 от egor"
        return f'Пост #{self.id} от {self.author.username}'

    # Свойство: количество лайков у поста
    # self.likes — QuerySet всех лайков (благодаря related_name='likes' в модели Like)
    # .count() — SQL-запрос COUNT(*) — считает строки без загрузки их в память
    @property
    def likes_count(self):
        return self.likes.count()

    # Свойство: количество комментариев у поста
    # self.comments — QuerySet всех комментариев (related_name='comments' в модели Comment)
    @property
    def comments_count(self):
        return self.comments.count()

    # Метод: проверяет, поставил ли конкретный пользователь лайк этому посту
    # Используется в view для подсветки кнопки лайка
    def is_liked_by(self, user):
        # Если пользователь не авторизован — он не мог ставить лайки
        if not user.is_authenticated:
            return False
        # .filter(user=user) — ищем лайк от этого пользователя
        # .exists() — возвращает True/False, не загружая данные в память (эффективнее)
        return self.likes.filter(user=user).exists()


# ============================================================
# МОДЕЛЬ: Comment (Комментарий)
# ============================================================
class Comment(models.Model):

    # Пост, к которому относится комментарий
    # on_delete=CASCADE — удалить пост = удалить все его комментарии
    # related_name='comments' — доступ: post.comments.all()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')

    # Автор комментария — ссылка на пользователя
    # related_name='comments' — доступ: user.comments.all() (все комментарии пользователя)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')

    # Текст комментария — неограниченной длины
    text = models.TextField(verbose_name='Текст комментария')

    # Время создания — ставится автоматически при сохранении
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Сортировка от старых к новым — комментарии идут в хронологическом порядке
        ordering = ['created_at']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        # Пример: "Комментарий egor к посту #5"
        return f'Комментарий {self.author.username} к посту #{self.post.id}'


# ============================================================
# МОДЕЛЬ: Like (Лайк)
# ============================================================
class Like(models.Model):

    # Пост, которому поставлен лайк
    # CASCADE — удалить пост = удалить все лайки на него
    # related_name='likes' — доступ: post.likes.all()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

    # Пользователь, который поставил лайк
    # related_name='likes' — доступ: user.likes.all()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')

    # Время постановки лайка
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # unique_together — комбинация (post, user) должна быть уникальной
        # Это гарантирует что один пользователь не может поставить лайк дважды
        # Django создаёт в БД UNIQUE constraint на эти два поля
        unique_together = ('post', 'user')
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'

    def __str__(self):
        # Пример: "Лайк egor на пост #3"
        return f'Лайк {self.user.username} на пост #{self.post.id}'
