# Используем легковесный и актуальный образ Python
FROM python:3.13-slim

# Запрещаем Python писать файлы кэша .pyc на диск и включаем немедленный вывод логов в консоль
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Устанавливаем системные утилиты, необходимые для сборки некоторых бинарных библиотек
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем зависимости проекта
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Копируем всю кодовую базу проекта в контейнер
COPY . .

# Открываем порт для FastAPI (воркеры порты наружу не выставляют)
EXPOSE 8000
