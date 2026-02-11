# TASK MANAGER

Полноценное веб-приложение для управления задачами с брутальным минималистичным дизайном.

##  Особенности

### Backend (FastAPI)
-  **JWT-авторизация**
-  **SQLAlchemy ORM**
-  **Argon2 хеширование**
-  **CRUD операции**
-  **Валидация данных**
-  **CORS middleware**
-  **Auto-документация**

### Frontend (Vanilla JS + HTML/CSS)
- **Vanilla JavaScript**
- **HTML5 + CSS3**

### Функционал
-  **Регистрация/Вход** - создание аккаунта и авторизация
-  **Создание задач** - добавление новых задач
-  **Смена статусов** - todo → in_progress → done
-  **Удаление задач** - с подтверждением
-  **Личный кабинет** - каждый пользователь видит только свои задачи

## Быстрый старт

### 1. Установить зависимости
```bash
pip install -r requirements.txt
```

### 2. Запустить сервер
```bash
# Вариант 1: через uvicorn
uvicorn app.main:app --reload

# Вариант 2: через python
python -m app.main
```

### 3. Открыть в браузере
- **Приложение:** http://127.0.0.1:8000/
- **API документация:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

## Структура проекта

```
Task-Manager-API-main/
├── app/
│   ├── __init__.py          # Инициализация пакета
│   ├── main.py              # FastAPI приложение, роуты
│   ├── models.py            # SQLAlchemy модели (User, Task)
│   ├── schemas.py           # Pydantic схемы для валидации
│   ├── crud.py              # Функции работы с БД
│   ├── auth.py              # JWT авторизация
│   ├── database.py          # Настройка подключения к БД
│   └── frontend/
│       └── index.html       # Фронтенд приложения
├── requirements.txt         # Python зависимости
├── test.db                  # SQLite база данных (создается автоматически)
└── README.md               # Этот файл
```

## Технологии

### Backend
- **FastAPI** - современный веб-фреймворк
- **SQLAlchemy** - ORM для работы с БД
- **Pydantic** - валидация данных
- **Passlib** - хеширование паролей (Argon2)
- **python-jose** - работа с JWT токенами
- **Uvicorn** - ASGI сервер

### Frontend
- **Vanilla JavaScript** - без фреймворков
- **HTML5 + CSS3** - семантическая верстка

### База данных
- **SQLite** - для разработки (можно заменить на PostgreSQL/MySQL)

## API Endpoints

### Аутентификация
```bash
POST /users/register     # Регистрация нового пользователя
POST /users/login        # Вход (получение JWT токена)
```

### Задачи (требуют авторизации)
```bash
GET    /tasks           # Список задач текущего пользователя
POST   /tasks           # Создать новую задачу
GET    /tasks/{id}      # Получить задачу по ID
PUT    /tasks/{id}      # Обновить задачу
DELETE /tasks/{id}      # Удалить задачу
```

## Примеры использования

### Регистрация пользователя
```bash
curl -X POST "http://127.0.0.1:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret123"}'
```

### Вход
```bash
curl -X POST "http://127.0.0.1:8000/users/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=secret123"
```

### Создание задачи
```bash
curl -X POST "http://127.0.0.1:8000/tasks" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Купить молоко"}'
```

### Получение задач
```bash
curl -X GET "http://127.0.0.1:8000/tasks" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Статусы задач:
- `[  ]` - TODO
- `[--]` - IN PROGRESS
- `[XX]` - DONE

## Безопасность

-  Пароли хешируются с использованием **Argon2**
-  JWT токены с временем жизни **8 часов**
-  CORS настроен (в продакшене нужно указать конкретные домены)
-  В продакшене обязательно измените `SECRET_KEY`!

##  Возможные улучшения

- [ ] Пагинация списка задач
- [ ] Фильтрация и сортировка
- [ ] Теги и категории для задач
- [ ] Дедлайны с уведомлениями
- [ ] Миграции через Alembic
- [ ] Docker + docker-compose
- [ ] Тесты (pytest)
- [ ] CI/CD pipeline
- [ ] WebSocket для real-time обновлений
- [ ] Роли пользователей (admin, user)

##  Автор

Создано для практики FastAPI, SQLAlchemy и JWT авторизации.

---

**TASK MANAGER** / 2025 / ВСЕ ПРАВА ЗАЩИЩЕНЫ
