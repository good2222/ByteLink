import os
# Импортируем модуль os для работы с операционной системой (переменные среды, пути и т.д.)

from pathlib import Path
# Импортируем класс Path из модуля pathlib для удобной работы с путями файловой системы

import environ
# Импортируем библиотеку django-environ для чтения переменных окружения из .env-файла

BASE_DIR = Path(__file__).resolve().parent.parent
# BASE_DIR — корневая директория проекта.
# Path(__file__) — путь к текущему файлу (settings.py).
# .resolve() — преобразует путь в абсолютный, убирая символические ссылки.
# .parent.parent — поднимаемся на два уровня вверх (из папки social_network/ в корень проекта).

env = environ.Env(
    # Создаём объект Env с явным указанием типов и значений по умолчанию для каждой переменной окружения.
    DEBUG=(bool, False),
    # DEBUG — режим отладки Django; тип bool, по умолчанию False (продакшн-режим).
    SECRET_KEY=(str, 'django-insecure-default-key-for-bytelink-2026'),
    # SECRET_KEY — секретный ключ Django для криптографии; тип str, заглушка по умолчанию.
    DB_ENGINE=(str, 'mysql'),
    # DB_ENGINE — тип базы данных ('mysql' или 'sqlite'); по умолчанию 'mysql'.
    DB_NAME=(str, 'bytelink'),
    # DB_NAME — имя базы данных; по умолчанию 'bytelink'.
    DB_USER=(str, 'root'),
    # DB_USER — пользователь базы данных; по умолчанию 'root'.
    DB_PASSWORD=(str, ''),
    # DB_PASSWORD — пароль пользователя БД; по умолчанию пустая строка.
    DB_HOST=(str, '127.0.0.1'),
    # DB_HOST — хост сервера базы данных; по умолчанию локальный адрес.
    DB_PORT=(str, '3306'),
    # DB_PORT — порт сервера базы данных; 3306 — стандартный порт MySQL.
)

env_file = BASE_DIR / '.env'
# Формируем полный путь к файлу .env в корне проекта с помощью оператора /

if env_file.exists():
    # Проверяем, существует ли файл .env на диске
    environ.Env.read_env(env_file)
    # Если файл существует — читаем из него переменные окружения и загружаем их в os.environ

SECRET_KEY = env('SECRET_KEY')
# Читаем значение SECRET_KEY из переменных окружения (или берём значение по умолчанию из environ.Env)

DEBUG = env.bool('DEBUG', default=True)
# Читаем DEBUG как булево значение; default=True означает режим разработки, если переменная не задана

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])
# ALLOWED_HOSTS — список хостов, которым разрешено обращаться к Django-приложению.
# env.list() парсит строку с запятыми в список Python; по умолчанию только локальные адреса.

INSTALLED_APPS = [
    # Список всех установленных Django-приложений в проекте.
    'daphne',
    # daphne — ASGI-сервер для обработки WebSocket и HTTP/2; должен быть первым для корректной работы.
    'django.contrib.admin',
    # django.contrib.admin — встроенная административная панель Django.
    'django.contrib.auth',
    # django.contrib.auth — встроенная система аутентификации и авторизации пользователей.
    'django.contrib.contenttypes',
    # django.contrib.contenttypes — фреймворк для работы с типами контента (generic relations).
    'django.contrib.sessions',
    # django.contrib.sessions — поддержка сессий пользователей (хранение состояния между запросами).
    'django.contrib.messages',
    # django.contrib.messages — система flash-сообщений (одноразовые уведомления для пользователя).
    'django.contrib.staticfiles',
    # django.contrib.staticfiles — управление статическими файлами (CSS, JS, изображения).
    'channels',
    # channels — Django Channels, расширение Django для работы с WebSocket и асинхронными протоколами.
    'apps.users.apps.UsersConfig',
    # Приложение пользователей ByteLink (регистрация, профиль, авторизация).
    'apps.posts.apps.PostsConfig',
    # Приложение постов (создание, просмотр, лента публикаций).
    'apps.chats.apps.ChatsConfig',
    # Приложение чатов (личные сообщения в реальном времени через WebSocket).
    'apps.groups.apps.GroupsConfig',
    # Приложение групп (сообщества пользователей).
    'apps.notifications.apps.NotificationsConfig',
    # Приложение уведомлений (оповещения о событиях: лайки, комментарии и т.д.).
]

MIDDLEWARE = [
    # Список middleware-компонентов, которые обрабатывают каждый HTTP-запрос/ответ по порядку.
    'django.middleware.security.SecurityMiddleware',
    # SecurityMiddleware — добавляет заголовки безопасности (HSTS, XSS-защита и т.д.).
    'django.contrib.sessions.middleware.SessionMiddleware',
    # SessionMiddleware — управляет сессиями пользователей (должен быть перед CommonMiddleware).
    'django.middleware.common.CommonMiddleware',
    # CommonMiddleware — выполняет общие операции: нормализация URL, запрет запрещённых агентов.
    'django.middleware.csrf.CsrfViewMiddleware',
    # CsrfViewMiddleware — защита от межсайтовой подделки запросов (CSRF-токены в формах).
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # AuthenticationMiddleware — привязывает объект пользователя к каждому запросу (request.user).
    'django.contrib.messages.middleware.MessageMiddleware',
    # MessageMiddleware — поддержка flash-сообщений между запросами.
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # XFrameOptionsMiddleware — защита от clickjacking: запрещает встраивать страницы через <iframe>.
]

ROOT_URLCONF = 'social_network.urls'
# Указывает модуль с корневыми URL-маршрутами проекта (файл social_network/urls.py).

TEMPLATES = [
    # Список конфигураций шаблонизаторов (обычно используется один — встроенный Django).
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # BACKEND — указывает движок шаблонов; используем стандартный Django Template Language (DTL).
        'DIRS': [BASE_DIR / 'templates'],
        # DIRS — список дополнительных директорий для поиска шаблонов (глобальная папка templates/).
        'APP_DIRS': True,
        # APP_DIRS=True — Django автоматически ищет шаблоны внутри папки templates/ каждого приложения.
        'OPTIONS': {
            # OPTIONS — дополнительные параметры движка шаблонов.
            'context_processors': [
                # context_processors — функции, добавляющие переменные в контекст каждого шаблона.
                'django.template.context_processors.debug',
                # Добавляет переменную debug в контекст шаблона (True/False в зависимости от DEBUG).
                'django.template.context_processors.request',
                # Добавляет объект request в контекст шаблона.
                'django.contrib.auth.context_processors.auth',
                # Добавляет объект user и perms (права) в контекст шаблона.
                'django.contrib.messages.context_processors.messages',
                # Добавляет flash-сообщения в контекст шаблона для отображения в HTML.
            ],
        },
    },
]

WSGI_APPLICATION = 'social_network.wsgi.application'
# Путь к WSGI-приложению для синхронных HTTP-серверов (gunicorn, uWSGI и т.д.).

ASGI_APPLICATION = 'social_network.asgi.application'
# Путь к ASGI-приложению для асинхронных серверов (daphne, uvicorn) — нужно для WebSocket.

DB_ENGINE = env('DB_ENGINE', default='mysql')
# Читаем тип СУБД из переменных окружения; используется для выбора конфигурации базы данных ниже.

if DB_ENGINE == 'sqlite':
    # Если выбран движок SQLite (обычно для локальной разработки без MySQL)
    DATABASES = {
        # Словарь конфигурации баз данных Django
        'default': {
            # 'default' — имя подключения по умолчанию (используется везде в коде)
            'ENGINE': 'django.db.backends.sqlite3',
            # ENGINE — бэкенд базы данных: встроенный SQLite (файловая БД, не требует сервера).
            'NAME': BASE_DIR / 'db.sqlite3',
            # NAME — путь к файлу базы данных SQLite в корне проекта.
        }
    }
else:
    # Иначе (по умолчанию) используем MySQL как основную СУБД
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            # ENGINE — бэкенд MySQL для Django (требует установки mysqlclient или PyMySQL).
            'NAME': env('DB_NAME'),
            # NAME — имя базы данных, читается из переменных окружения.
            'USER': env('DB_USER'),
            # USER — имя пользователя MySQL, читается из переменных окружения.
            'PASSWORD': env('DB_PASSWORD'),
            # PASSWORD — пароль пользователя MySQL, читается из переменных окружения.
            'HOST': env('DB_HOST'),
            # HOST — адрес сервера MySQL (IP или hostname), читается из переменных окружения.
            'PORT': env('DB_PORT'),
            # PORT — порт сервера MySQL, читается из переменных окружения.
            'OPTIONS': {'charset': 'utf8mb4'}
            # OPTIONS — дополнительные параметры подключения к MySQL.
            # charset='utf8mb4' — полная поддержка Unicode включая эмодзи (4-байтный UTF-8).
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    # Список валидаторов паролей — проверяют надёжность пароля при регистрации/смене пароля.
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    # UserAttributeSimilarityValidator — запрещает пароли, похожие на имя пользователя, email и т.д.
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    # MinimumLengthValidator — проверяет минимальную длину пароля (по умолчанию 8 символов).
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    # CommonPasswordValidator — запрещает наиболее распространённые пароли ('password', '123456' и др.).
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    # NumericPasswordValidator — запрещает полностью числовые пароли (например '12345678').
]

LANGUAGE_CODE = 'ru'
# Код языка по умолчанию — русский; влияет на переводы интерфейса Django и даты.

TIME_ZONE = 'Europe/Kiev'
# Часовой пояс проекта — Киев (UTC+2/UTC+3); используется для хранения и отображения времени.

USE_I18N = True
# USE_I18N=True — включает систему интернационализации Django (перевод строк интерфейса).

USE_TZ = True
# USE_TZ=True — Django хранит все даты/время в UTC в базе данных и конвертирует при отображении.

STATIC_URL = '/static/'
# URL-префикс для обращения к статическим файлам из браузера (например /static/css/style.css).

STATICFILES_DIRS = [BASE_DIR / 'static']
# Список дополнительных директорий, где Django ищет статические файлы во время разработки.

STATIC_ROOT = BASE_DIR / 'staticfiles'
# Директория, куда команда collectstatic собирает все статические файлы для продакшна.

MEDIA_URL = '/media/'
# URL-префикс для медиафайлов, загружаемых пользователями (аватары, вложения и т.д.).

MEDIA_ROOT = BASE_DIR / 'media'
# Директория на диске, куда сохраняются загружаемые пользователями медиафайлы.

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Тип поля первичного ключа по умолчанию для всех моделей — BigAutoField (64-битный автоинкремент).

AUTH_USER_MODEL = 'users.CustomUser'
# Указывает кастомную модель пользователя вместо стандартной django.contrib.auth.models.User.
# 'users.CustomUser' — модель CustomUser из приложения users.

CHANNEL_LAYERS = {
    # Конфигурация слоёв каналов для Django Channels (WebSocket, группы каналов).
    'default': {
        # 'default' — имя слоя каналов по умолчанию.
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
        # InMemoryChannelLayer — хранит сообщения каналов в памяти процесса.
        # Подходит только для разработки; в продакшне следует использовать RedisChannelLayer.
    },
}

LOGIN_URL = 'login'
# URL (по имени маршрута), на который перенаправляется неаутентифицированный пользователь.

LOGIN_REDIRECT_URL = 'home'
# URL (по имени маршрута), на который перенаправляется пользователь после успешного входа.

LOGOUT_REDIRECT_URL = 'login'
# URL (по имени маршрута), на который перенаправляется пользователь после выхода из системы.
