from django.urls import path
# Импортируем функцию path для создания URL-маршрутов (паттерн строки → класс/функция-представление).

from django.contrib.auth import views as auth_views
# Импортируем встроенные представления Django для аутентификации (вход, выход, смена пароля и т.д.)
# и даём им псевдоним auth_views для удобства обращения.

from .views import RegisterView, ProfileView, ProfileEditView
# Импортируем кастомные класс-представления из файла views.py текущего приложения (apps/users/):
# RegisterView — регистрация нового пользователя.
# ProfileView — просмотр профиля пользователя.
# ProfileEditView — редактирование профиля текущего пользователя.

urlpatterns = [
    # urlpatterns — список маршрутов приложения users, который подключается в главном urls.py через include().

    path('register/', RegisterView.as_view(), name='register'),
    # Маршрут '/register/' — страница регистрации нового аккаунта.
    # RegisterView.as_view() — преобразует класс в вызываемый обработчик запросов.
    # name='register' — именованный маршрут для использования в {% url 'register' %} и redirect().

    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # Маршрут '/login/' — страница входа в систему.
    # Используем встроенный LoginView от Django (обрабатывает форму входа, сессии, CSRF).
    # template_name='registration/login.html' — переопределяем шаблон: используем собственный HTML-файл.
    # name='login' — именованный маршрут; также используется в настройке LOGIN_URL в settings.py.

    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    # Маршрут '/logout/' — выход из системы.
    # Используем встроенный LogoutView от Django (завершает сессию пользователя).
    # next_page='login' — после выхода перенаправляет пользователя на страницу входа (маршрут 'login').
    # name='logout' — именованный маршрут.

    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    # Маршрут '/profile/edit/' — страница редактирования профиля авторизованного пользователя.
    # ProfileEditView — кастомное представление с формой изменения данных (имя, аватар, биография и т.д.).
    # ВАЖНО: этот маршрут должен быть объявлен ДО маршрута с <str:username>,
    # иначе строка 'edit' будет воспринята как username.
    # name='profile_edit' — именованный маршрут.

    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    # Маршрут '/profile/<username>/' — страница просмотра профиля любого пользователя.
    # <str:username> — динамический фрагмент URL: захватывает строку и передаёт в представление
    # как именованный аргумент username (например /profile/john/ → username='john').
    # ProfileView — кастомное представление, отображающее публичный профиль указанного пользователя.
    # name='profile' — именованный маршрут; используется как {% url 'profile' username=user.username %}.
]
