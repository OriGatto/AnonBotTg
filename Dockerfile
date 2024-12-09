# Используем официальный образ Python как базовый образ
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем зависимости проекта в рабочую директорию
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt || \
    (echo "Failed to install dependencies. Contents of requirements.txt:" && \
     cat /app/requirements.txt && \
     exit 1)

# Копируем весь код проекта в рабочую директорию
COPY . .

# Запускаем бота
CMD ["python", "anonymous_questions_bot.py"]