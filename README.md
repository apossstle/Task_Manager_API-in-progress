# Task Manager API (skeleton)

Backend-проект для практики SQL, ORM и токен-авторизации.

## Быстрый старт
1. Создать виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/bin/activate  # linux / mac
   venv\\Scripts\\activate   # windows (powershell)
   ```
2. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Запустить приложение:
   ```bash
   uvicorn app.main:app --reload
   ```
4. Открыть документацию: http://127.0.0.1:8000/docs

## Чеклист для улучшения
- Примеры запросов (curl / httpie)
- Добавить пагинацию/фильтрацию задач
- Роли (admin) и ограничения
- Миграции (alembic)
- Docker + Postgres
- Тесты (pytest)
