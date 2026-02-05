# Task Tracker (FastAPI + PostgreSQL)

Сервис для трекинга задач с CRUD, фильтрацией, сменой статуса и аналитикой.

## Стек
- FastAPI
- PostgreSQL
- SQLAlchemy + Alembic
- pandas + matplotlib/seaborn (аналитика)
- Pytest

## Быстрый старт

### 1) Установка зависимостей
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Запуск PostgreSQL
```bash
docker compose up -d
```

### 3) Настройка окружения
По умолчанию используется:
```
postgresql+psycopg2://postgres:postgres@localhost:5432/task_tracker
```
Если нужно другое значение, создайте файл `.env`:
```
APP_DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/task_tracker
```

### 4) Миграции
```bash
alembic upgrade head
```

### 5) Запуск API
```bash
uvicorn app.main:app --reload
```
Документация: http://localhost:8000/docs

## Основные эндпойнты

### Регистрация пользователя
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","full_name":"Admin User","password":"secret123"}'
```

### Логин (получить токен)
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"secret123"}'
```
Используйте полученный `token` в Swagger UI (кнопка **Authorize**) или в заголовке `Authorization: Bearer <TOKEN>`.

### Создание задачи
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Сделать отчёт","description":"Подготовить аналитическую сводку","status":"new","topic":"аналитика"}'
```

### Фильтрация
```bash
curl -X GET "http://localhost:8000/tasks?status=done&topic=аналитика" \
  -H "Authorization: Bearer <TOKEN>"
```

### Смена статуса
```bash
curl -X PATCH http://localhost:8000/tasks/1/status \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '"in_progress"'
```

### Аналитика
```bash
curl -X GET "http://localhost:8000/tasks/analytics?group_by=status&with_chart=true" \
  -H "Authorization: Bearer <TOKEN>"
```
Ответ содержит JSON и (опционально) base64 изображение графика.

## Тесты
```bash
pytest
```

## Примечания по безопасности
- Используется токен-авторизация через заголовок `Authorization: Bearer <TOKEN>`.
- Пароли хэшируются (bcrypt).
- SQL-инъекции предотвращаются использованием ORM.
