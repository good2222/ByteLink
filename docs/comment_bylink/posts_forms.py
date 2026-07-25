# ============================================================
# ФАЙЛ: apps/posts/forms.py
# Формы для создания постов и комментариев
# ============================================================

# Импортируем модуль forms из Django — он содержит всё необходимое для работы с формами
from django import forms

# Импортируем модели Post и Comment из текущего приложения
# Они нужны, чтобы форма знала, в какую таблицу БД сохранять данные
from .models import Post, Comment


# ---- Форма для создания поста ----
class PostForm(forms.ModelForm):
    # ModelForm — специальный тип формы, который автоматически создаётся из модели
    # Он сам знает, какие поля и их типы нужны — на основе модели Post

    class Meta:
        # Указываем, на основе какой модели строится форма
        model = Post

        # Список полей, которые будут отображаться в форме
        # 'content' — текст поста, 'image' — прикреплённое изображение
        fields = ['content', 'image']

        # widgets — позволяют настроить HTML-атрибуты каждого поля формы
        widgets = {
            # Поле 'content' отображается как многострочный текстовый блок (textarea)
            'content': forms.Textarea(attrs={
                'class': 'form-control',     # Bootstrap CSS класс для стилизации
                'rows': 3,                   # Высота поля — 3 строки
                'placeholder': 'Что у вас нового?',  # Подсказка внутри поля
                'required': True             # Поле обязательно для заполнения
            }),
            # Поле 'image' отображается как кнопка выбора файла
            'image': forms.FileInput(attrs={
                'class': 'form-control',     # Bootstrap CSS класс
                'accept': 'image/*'          # Браузер разрешает выбирать только изображения
            })
        }


# ---- Форма для создания комментария ----
class CommentForm(forms.ModelForm):
    # Аналогично PostForm, но для модели Comment

    class Meta:
        # Форма строится на основе модели Comment
        model = Comment

        # Отображаем только поле 'text' — сам текст комментария
        # Поля 'post' и 'author' заполняются автоматически во view, не в форме
        fields = ['text']

        widgets = {
            # Поле 'text' — однострочный текстовый ввод (input type="text")
            'text': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',   # Маленький Bootstrap input
                'placeholder': 'Напишите комментарий...',  # Подсказка внутри поля
                'required': True                           # Поле обязательно
            })
        }
