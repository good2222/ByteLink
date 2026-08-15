# =====================================================================
# ФАЙЛ: apps/users/context_processors.py
# Контекстный процессор для полной локализации сайта (RU / UA)
# =====================================================================

TRANSLATIONS = {
    'ru': {
        # Навигация и Шапка
        'brand': 'ByteLink',
        'feed': 'Лента',
        'friends': 'Друзья',
        'groups': 'Группы',
        'messages': 'Сообщения',
        'notifications': 'Уведомления',
        'my_profile': 'Мой профиль',
        'profile': 'Профиль',
        'settings': 'Настройки',
        'admin_panel': 'Админ-панель',
        'logout': 'Выйти',
        'login': 'Войти',
        'register': 'Регистрация',
        'search_placeholder': 'Поиск пользователей...',
        'search': 'Поиск',

        # Посты и Лента
        'what_new': 'Что у вас нового?',
        'publish': 'Опубликовать',
        'attach_photo': 'Прикрепить фото',
        'like': 'Нравится',
        'comment': 'Комментировать',
        'comments': 'Комментарии',
        'add_comment': 'Написать комментарий...',
        'send': 'Отправить',
        'delete_post': 'Удалить публикацию',
        'delete_comment': 'Удалить комментарий',
        'empty_feed_title': 'Лента пуста',
        'empty_feed_text': 'Будьте первым — опубликуйте что-нибудь!',
        'posts': 'Публикации',
        'post': 'Публикация',
        'friends_feed': 'Посты друзей',
        'all_feed': 'Все записи',
        'other_feed': 'Все авторы',
        'page': 'Страница',
        'of': 'из',
        'prev': 'Назад',
        'next': 'Далее',

        # Друзья и Профиль
        'add_friend': 'Добавить в друзья',
        'remove_friend': 'Удалить из друзей',
        'request_sent': 'Заявка отправлена',
        'accept': 'Принять',
        'decline': 'Отклонить',
        'write_message': 'Написать',
        'edit_profile': 'Редактировать профиль',
        'bio': 'О себе',
        'status': 'Статус',
        'location': 'Местоположение',
        'website': 'Сайт',
        'birth_date': 'Дата рождения',
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'avatar': 'Аватар',
        'cover': 'Обложка',
        'incoming_requests': 'Входящие заявки',
        'no_friend_requests': 'Заявок в друзья нет',
        'no_friends': 'У вас пока нет друзей',
        'my_friends': 'Мои друзья',

        # Группы
        'subscribers': 'Участники',
        'create_group': 'Создать группу',
        'edit_group': 'Редактировать группу',
        'delete_group': 'Удалить группу',
        'join_group': 'Вступить в группу',
        'leave_group': 'Выйти из группы',
        'group_members': 'Участники группы',
        'group_posts': 'Публикации группы',
        'group_title': 'Название группы',
        'group_description': 'Описание группы',
        'no_groups': 'Вы пока не состоите ни в одной группе',
        'my_groups': 'Мои группы',
        'all_groups': 'Все группы',
        'open': 'Открыть',
        'open_group': 'Перейти в группу',

        # Чаты и Сообщения
        'start_chat': 'Начать диалог',
        'enter_message': 'Введите сообщение...',
        'no_messages_yet': 'В этом чате пока нет сообщений',
        'no_chats': 'У вас пока нет активных диалогов',
        'online': 'В сети',

        # Уведомления
        'no_notifications': 'Уведомлений пока нет',
        'mark_read': 'Отметить все как прочитанные',
        'all_notifications': 'Все действия и события вашей страницы',

        # Авторизация и Поиск
        'username': 'Имя пользователя',
        'password': 'Пароль',
        'email': 'Email адрес',
        'already_account': 'Уже есть аккаунт?',
        'no_account': 'Нет аккаунта?',
        'no_results': 'По вашему запросу ничего не найдено',
        'search_results': 'Результаты поиска',

        # Общие кнопки
        'save': 'Сохранить',
        'cancel': 'Отмена',
        'delete': 'Удалить',
        'edit': 'Редактировать',
        'back': 'Назад',
    },
    'uk': {
        # Навігація та Шапка
        'brand': 'ByteLink',
        'feed': 'Стрічка',
        'friends': 'Друзі',
        'groups': 'Групи',
        'messages': 'Повідомлення',
        'notifications': 'Сповіщення',
        'my_profile': 'Мій профіль',
        'profile': 'Профіль',
        'settings': 'Налаштування',
        'admin_panel': 'Адмін-панель',
        'logout': 'Вийти',
        'login': 'Увійти',
        'register': 'Реєстрація',
        'search_placeholder': 'Пошук користувачів...',
        'search': 'Пошук',

        # Пости та Стрічка
        'what_new': 'Що у вас нового?',
        'publish': 'Опублікувати',
        'attach_photo': 'Прикріпити фото',
        'like': 'Подобається',
        'comment': 'Коментувати',
        'comments': 'Коментарі',
        'add_comment': 'Написати коментар...',
        'send': 'Надіслати',
        'delete_post': 'Видалити публікацію',
        'delete_comment': 'Видалити коментар',
        'empty_feed_title': 'Стрічка порожня',
        'empty_feed_text': 'Будьте першим — опублікуйте що-небудь!',
        'posts': 'Публікації',
        'post': 'Публікація',
        'friends_feed': 'Пості друзів',
        'all_feed': 'Усі записи',
        'other_feed': 'Усі автори',
        'page': 'Сторінка',
        'of': 'з',
        'prev': 'Назад',
        'next': 'Далі',

        # Друзі та Профіль
        'add_friend': 'Додати до друзів',
        'remove_friend': 'Видалити з друзів',
        'request_sent': 'Заявку надіслано',
        'accept': 'Прийняти',
        'decline': 'Відхилити',
        'write_message': 'Написати',
        'edit_profile': 'Редагувати профіль',
        'bio': 'Про себе',
        'status': 'Статус',
        'location': 'Місцезнаходження',
        'website': 'Сайт',
        'birth_date': 'Дата народження',
        'first_name': "Ім'я",
        'last_name': 'Прізвище',
        'avatar': 'Аватар',
        'cover': 'Обкладинка',
        'incoming_requests': 'Вхідні заявки',
        'no_friend_requests': 'Заявок у друзі немає',
        'no_friends': 'У вас поки немає друзів',
        'my_friends': 'Мої друзі',

        # Групи
        'subscribers': 'Учасники',
        'create_group': 'Створити групу',
        'edit_group': 'Редагувати групу',
        'delete_group': 'Видалити групу',
        'join_group': 'Вступити в групу',
        'leave_group': 'Вийти з групи',
        'group_members': 'Учасники групи',
        'group_posts': 'Публікації групи',
        'group_title': 'Назва групи',
        'group_description': 'Опис групи',
        'no_groups': 'Ви поки не перебуваєте в жодній групі',
        'my_groups': 'Мої групи',
        'all_groups': 'Усі групи',
        'open': 'Відкрити',
        'open_group': 'Перейти до групи',

        # Чати та Повідомлення
        'start_chat': 'Розпочати діалог',
        'enter_message': 'Введіть повідомлення...',
        'no_messages_yet': 'У цьому чаті поки немає повідомлень',
        'no_chats': 'У вас поки немає активних діалогів',
        'online': 'В мережі',

        # Сповіщення
        'no_notifications': 'Сповіщень поки немає',
        'mark_read': 'Позначити всі як прочитані',
        'all_notifications': 'Усі дії та події вашої сторінки',

        # Авторизація та Пошук
        'username': "Ім'я користувача",
        'password': 'Пароль',
        'email': 'Email адреса',
        'already_account': 'Вже є акаунт?',
        'no_account': 'Немає акаунту?',
        'no_results': 'За вашим запитом нічого не знайдено',
        'search_results': 'Результати пошуку',

        # Загальні кнопки
        'save': 'Зберегти',
        'cancel': 'Скасувати',
        'delete': 'Видалити',
        'edit': 'Редагувати',
        'back': 'Назад',
    }
}


def translation_processor(request):
    """
    Автоматически передаёт объект переводов `t` во все HTML-шаблоны сайта
    в зависимости от языка, выбранного пользователем в сессии.
    """
    lang = request.session.get('django_language', 'uk')  # По умолчанию Украинский язык
    if lang not in TRANSLATIONS:
        lang = 'uk'
    return {
        't': TRANSLATIONS[lang],
        'current_lang': lang
    }
