from django.contrib import admin
# Импортируем модуль admin из Django для подключения встроенной административной панели.

from django.urls import path, include
# path — функция для создания одного URL-маршрута (паттерн → представление).
# include — функция для подключения URL-маршрутов из другого модуля (вложенные urls.py).

from django.conf import settings
# Импортируем объект настроек проекта Django для доступа к параметрам (DEBUG, MEDIA_URL и т.д.).

from django.conf.urls.static import static
# Функция static() генерирует URL-маршруты для раздачи медиа- и статических файлов в режиме разработки.

from apps.users.views import HomeView
# Импортируем класс-представление HomeView из приложения users — это главная страница сайта.

urlpatterns = [
    # urlpatterns — специальный список, в котором Django ищет подходящий маршрут для каждого запроса.
    path('admin/', admin.site.urls),
    # Маршрут '/admin/' подключает стандартную административную панель Django.
    # admin.site.urls — встроенный набор URL-адресов для работы с /admin/.

    path('', HomeView.as_view(), name='home'),
    # Маршрут для корневого URL '/' (пустая строка).
    # HomeView.as_view() — преобразует класс-представление в функцию-обработчик запроса.
    # name='home' — именованный маршрут, используется в шаблонах через {% url 'home' %}.

    path('', include('apps.users.urls')),
    # Подключает все URL-маршруты из файла apps/users/urls.py с корневым префиксом ''.
    # Это добавляет маршруты регистрации, входа, профиля и т.д. без дополнительного префикса.

    path('', include('apps.posts.urls')),
    # Подключает все URL-маршруты из файла apps/posts/urls.py с корневым префиксом ''.
    # Добавляет маршруты для создания, просмотра и управления постами.
]

if settings.DEBUG:
    # Следующие маршруты добавляются ТОЛЬКО в режиме разработки (DEBUG=True).
    # В продакшне раздачей медиа и статики занимается веб-сервер (nginx, apache).

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Добавляем маршруты для раздачи медиафайлов (загруженных пользователями файлов).
    # settings.MEDIA_URL — URL-префикс ('/media/'), document_root — реальная папка на диске.
    # Без этого строки загруженные аватары и изображения не откроются в браузере при разработке.

    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
    # Добавляем маршруты для раздачи статических файлов (CSS, JS, изображений темы).
    # settings.STATIC_URL — URL-префикс ('/static/'), document_root — папка static/ в корне проекта.
