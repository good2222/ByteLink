# Використовуємо офіційний легкий образ Python 3.12 Slim
FROM python:3.12-slim

# Системні залежності для компіляції пакетів (Pillow, MySQL, CFFI тощо)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Вимикаємо буферизацію логів та створення .pyc файлів
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Робоча директорія в контейнері
WORKDIR /app

# Копіюємо файл залежностей для кешування Docker-шарів
COPY requirements.txt .

# Оновлюємо pip та встановлюємо залежності
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копіюємо код проекту
COPY . .

# Створюємо директорії для статичних файлів та медіа
RUN mkdir -p /app/staticfiles /app/media

# Відкриваємо порт 8000
EXPOSE 8000

# Запускаємо ASGI сервер Daphne (для підтримки HTTP та WebSockets)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "social_network.asgi:application"]