# FastAPI WebSocket PC Monitor

Сервер для мониторинга статуса удаленных ПК через WebSockets.

## Локальный запуск

1.  Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

2.  Запустите сервер:
    ```bash
    uvicorn main:app --reload
    ```
    Сервер будет доступен по адресу: `http://localhost:8000`

3.  Запустите тестового клиента (в новом терминале):
    ```bash
    python test_client.py "My-Gaming-PC"
    ```

## Деплой на Render.com

1.  Создайте "New Web Service" на Render.
2.  Подключите репозиторий с кодом.
3.  **Environment**: Python 3
4.  **Build Command**: `pip install -r requirements.txt`
5.  **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`

## Переменные окружения (Environment Variables)

Для работы уведомлений Telegram, добавьте эти переменные в настройках Render (Environment Variables):

- `BOT_TOKEN`: `8336385730:AAE9YGuk9_f-IC_s4R0nMCy0Pa8n_R6Rz9o`
- `ADMIN_CHAT_ID`: `740478354`

(В коде они сейчас "зашиты", но для безопасности лучше вынести их в `os.getenv`).

## Структура проекта

- `main.py`: Основной файл сервера.
- `database.py`: Работа с SQLite.
- `telegram_bot.py`: Отправка уведомлений.
- `templates/index.html`: Фронтенд (HTML).
- `static/`: Стили CSS и скрипты JS.
- `requirements.txt`: Список зависимостей.
