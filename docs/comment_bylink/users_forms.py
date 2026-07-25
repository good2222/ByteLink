# ============================================================
# ФАЙЛ: apps/users/forms.py
# Описание: Формы для регистрации пользователя и редактирования профиля
# ============================================================

# Импортируем модуль forms из Django — содержит базовые классы форм и поля
from django import forms

# UserCreationForm — встроенная Django-форма для создания пользователя
# Уже содержит поля username, password1, password2 и валидацию паролей
# UserChangeForm — форма для изменения данных существующего пользователя (для Admin)
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# Импортируем нашу модель пользователя — нужна для Meta класса
from .models import CustomUser


# ============================================================
# ФОРМА: CustomUserCreationForm — Регистрация нового пользователя
# Наследуется от UserCreationForm — добавляем только email
# ============================================================
class CustomUserCreationForm(UserCreationForm):

    # Добавляем поле email вручную — оно не входит по умолчанию в UserCreationForm
    # required=True — пользователь обязан ввести email при регистрации
    # label="Email" — подпись поля в HTML-форме
    email = forms.EmailField(required=True, label="Email")

    # Meta-класс описывает, с какой моделью работает форма и какие поля показывать
    class Meta(UserCreationForm.Meta):
        # Привязываем форму к нашей кастомной модели пользователя
        model = CustomUser
        # Показываем только username и email (password1/password2 добавляются автоматически из родителя)
        fields = ('username', 'email')

    # Переопределяем метод save() — вызывается при успешной валидации формы
    # commit=True — означает "сохранить в базу данных сразу"
    def save(self, commit=True):
        # Вызываем родительский save() с commit=False — создаём объект, но НЕ сохраняем в БД пока
        user = super().save(commit=False)

        # Проверяем: если в базе ещё нет ни одного пользователя — первый регистрирующийся становится админом
        if CustomUser.objects.count() == 0:
            user.role = 'admin'        # Назначаем роль администратора
            user.is_staff = True       # Даём доступ к Django Admin панели
            user.is_superuser = True   # Полные права суперпользователя (все разрешения)
        else:
            # Все остальные пользователи получают обычную роль
            user.role = 'user'

        # Если commit=True — сохраняем пользователя в базу данных
        if commit:
            user.save()

        # Возвращаем созданный объект пользователя
        return user


# ============================================================
# ФОРМА: CustomUserChangeForm — только для Django Admin
# Используется администратором для редактирования профилей
# ============================================================
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        # Привязка к нашей модели
        model = CustomUser
        # Список всех редактируемых полей в Admin-панели
        fields = ('username', 'email', 'role', 'bio', 'status_message', 'avatar', 'cover_image', 'birth_date', 'location', 'website')


# ============================================================
# ФОРМА: UserProfileForm — Редактирование профиля пользователем
# Показывается на странице /profile/edit/
# ============================================================
class UserProfileForm(forms.ModelForm):

    # ModelForm автоматически создаёт поля из указанных полей модели
    class Meta:
        # Привязка к модели пользователя
        model = CustomUser

        # Список полей для редактирования профиля
        # НЕ включаем username, password, role — они не должны меняться через этот экран
        fields = ('first_name', 'last_name', 'bio', 'status_message', 'avatar', 'cover_image', 'birth_date', 'location', 'website')

        # widgets — кастомизируем HTML-представление каждого поля
        widgets = {
            # Поле даты рождения: type="date" показывает календарь в браузере
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),

            # Поле "О себе": многострочный textarea, 3 строки высотой
            'bio': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Расскажите о себе...'
            }),

            # Поле имени: однострочный input с подсказкой
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),

            # Поле фамилии
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),

            # Поле статуса — короткая фраза ("Слушаю музыку", "На работе" и т.д.)
            'status_message': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Чем вы занимаетесь сегодня?'}),

            # Поле местоположения
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Город, Страна'}),

            # Поле сайта: URLInput — браузер подсказывает ввод URL
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
        }
