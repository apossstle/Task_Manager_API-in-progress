# 🗂️ Task Manager API v2

REST API для управления задачами с JWT-авторизацией, SQLite и полным фронтендом на TypeScript.

## 🚀 Быстрый старт

```bash
# Backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Открыть в браузере
# Вход/Регистрация: http://127.0.0.1:8000/
# Доска задач:      http://127.0.0.1:8000/board
# API документация: http://127.0.0.1:8000/docs
```

## 🧪 Тесты

```bash
pytest -v                              # все тесты
pytest --cov=app --cov-report=term     # с покрытием
pytest --html=report.html              # HTML-отчёт
```

## 📁 Структура

```
Task-Manager-API/
├── app/
│   ├── main.py           # FastAPI роуты
│   ├── models.py         # SQLAlchemy: User, Task
│   ├── schemas.py        # Pydantic схемы с валидацией
│   ├── crud.py           # Работа с БД + фильтры
│   ├── database.py       # SQLite подключение
│   ├── auth.py           # JWT авторизация
│   └── frontend/
│       ├── index.html    # Страница входа / регистрации
│       ├── tasks.html    # Доска задач
│       ├── tsconfig.json
│       └── src/          # TypeScript источники
│           ├── types.ts  # Типы и интерфейсы
│           ├── api.ts    # HTTP-клиент
│           ├── auth.ts   # Логика auth-страницы
│           └── tasks.ts  # Логика доски задач
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_tasks.py
│   └── test_integration.py
├── docs/
│   └── test_cases.md     # Ручные тест-кейсы
├── package.json          # TypeScript сборка
└── requirements.txt
```

## 📋 API

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/users/register` | Регистрация |
| POST | `/users/login` | Вход → JWT токен |
| GET | `/tasks?status=done&priority=3` | Задачи с фильтрами |
| POST | `/tasks` | Создать задачу |
| GET | `/tasks/{id}` | Задача по ID |
| PUT | `/tasks/{id}` | Обновить задачу |
| DELETE | `/tasks/{id}` | Удалить задачу |
