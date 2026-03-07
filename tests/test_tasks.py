"""
Тесты CRUD для задач. Все эндпоинты требуют JWT-токен.
"""
import pytest


class TestCreateTask:

    def test_create_task_success(self, client, auth_headers):
        resp = client.post("/tasks", json={"title": "Новая задача"}, headers=auth_headers)
        assert resp.status_code == 201

    def test_create_task_response_fields(self, client, auth_headers):
        data = client.post("/tasks", json={"title": "Задача"}, headers=auth_headers).json()
        assert all(k in data for k in ("id", "title", "status", "priority", "owner_id"))

    def test_create_task_default_status_is_todo(self, client, auth_headers):
        data = client.post("/tasks", json={"title": "Задача"}, headers=auth_headers).json()
        assert data["status"] == "todo"

    def test_create_task_default_priority_is_2(self, client, auth_headers):
        data = client.post("/tasks", json={"title": "Задача"}, headers=auth_headers).json()
        assert data["priority"] == 2

    def test_create_task_with_priority(self, client, auth_headers):
        data = client.post("/tasks", json={"title": "Срочно", "priority": 3}, headers=auth_headers).json()
        assert data["priority"] == 3

    def test_create_task_without_auth_returns_401(self, client):
        resp = client.post("/tasks", json={"title": "Задача"})
        assert resp.status_code == 401

    def test_create_task_empty_title_returns_422(self, client, auth_headers):
        resp = client.post("/tasks", json={"title": ""}, headers=auth_headers)
        assert resp.status_code == 422

    def test_create_task_missing_title_returns_422(self, client, auth_headers):
        resp = client.post("/tasks", json={"description": "без title"}, headers=auth_headers)
        assert resp.status_code == 422

    @pytest.mark.parametrize("priority", [0, 4, -1, 99])
    def test_create_task_invalid_priority_returns_422(self, client, auth_headers, priority):
        resp = client.post("/tasks", json={"title": "T", "priority": priority}, headers=auth_headers)
        assert resp.status_code == 422

    @pytest.mark.parametrize("priority", [1, 2, 3])
    def test_create_task_valid_priorities(self, client, auth_headers, priority):
        resp = client.post("/tasks", json={"title": "T", "priority": priority}, headers=auth_headers)
        assert resp.status_code == 201

    def test_create_task_invalid_token_returns_401(self, client):
        resp = client.post("/tasks", json={"title": "T"}, headers={"Authorization": "Bearer fake.token.here"})
        assert resp.status_code == 401


class TestGetTasks:

    def test_get_tasks_empty_returns_list(self, client, auth_headers):
        data = client.get("/tasks", headers=auth_headers).json()
        assert isinstance(data, list) and len(data) == 0

    def test_get_tasks_returns_created_tasks(self, client, auth_headers):
        client.post("/tasks", json={"title": "T1"}, headers=auth_headers)
        client.post("/tasks", json={"title": "T2"}, headers=auth_headers)
        data = client.get("/tasks", headers=auth_headers).json()
        assert len(data) == 2

    def test_get_tasks_without_auth_returns_401(self, client):
        assert client.get("/tasks").status_code == 401

    def test_get_tasks_filter_by_priority(self, client, auth_headers):
        client.post("/tasks", json={"title": "Low", "priority": 1}, headers=auth_headers)
        client.post("/tasks", json={"title": "High", "priority": 3}, headers=auth_headers)
        data = client.get("/tasks?priority=3", headers=auth_headers).json()
        assert len(data) == 1 and data[0]["priority"] == 3

    def test_get_tasks_filter_by_status(self, client, auth_headers, created_task):
        # Обновляем статус одной задачи
        client.put(f"/tasks/{created_task['id']}", json={"status": "done"}, headers=auth_headers)
        client.post("/tasks", json={"title": "Ещё одна"}, headers=auth_headers)

        done_tasks = client.get("/tasks?status=done", headers=auth_headers).json()
        todo_tasks = client.get("/tasks?status=todo", headers=auth_headers).json()

        assert len(done_tasks) == 1
        assert len(todo_tasks) == 1

    def test_user_sees_only_own_tasks(self, client, auth_headers, second_user_headers):
        """Пользователь не должен видеть задачи других пользователей."""
        client.post("/tasks", json={"title": "Моя задача"}, headers=auth_headers)
        client.post("/tasks", json={"title": "Чужая задача"}, headers=second_user_headers)

        my_tasks = client.get("/tasks", headers=auth_headers).json()
        assert len(my_tasks) == 1
        assert my_tasks[0]["title"] == "Моя задача"


class TestGetTaskById:

    def test_get_task_by_id_success(self, client, auth_headers, created_task):
        resp = client.get(f"/tasks/{created_task['id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == created_task["id"]

    def test_get_task_nonexistent_returns_404(self, client, auth_headers):
        assert client.get("/tasks/9999", headers=auth_headers).status_code == 404

    def test_get_task_of_other_user_returns_404(self, client, auth_headers, second_user_headers):
        """Нельзя получить чужую задачу — должен быть 404, а не 403 (не раскрываем существование)."""
        task = client.post("/tasks", json={"title": "Чужая"}, headers=second_user_headers).json()
        resp = client.get(f"/tasks/{task['id']}", headers=auth_headers)
        assert resp.status_code == 404

    def test_get_task_without_auth_returns_401(self, client, auth_headers, created_task):
        resp = client.get(f"/tasks/{created_task['id']}")
        assert resp.status_code == 401


class TestUpdateTask:

    def test_update_task_title(self, client, auth_headers, created_task):
        resp = client.put(f"/tasks/{created_task['id']}", json={"title": "Обновлено"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["title"] == "Обновлено"

    def test_update_task_status_to_in_progress(self, client, auth_headers, created_task):
        resp = client.put(f"/tasks/{created_task['id']}", json={"status": "in_progress"}, headers=auth_headers)
        assert resp.json()["status"] == "in_progress"

    def test_update_task_status_to_done(self, client, auth_headers, created_task):
        resp = client.put(f"/tasks/{created_task['id']}", json={"status": "done"}, headers=auth_headers)
        assert resp.json()["status"] == "done"

    def test_update_task_priority(self, client, auth_headers, created_task):
        resp = client.put(f"/tasks/{created_task['id']}", json={"priority": 3}, headers=auth_headers)
        assert resp.json()["priority"] == 3

    def test_update_task_nonexistent_returns_404(self, client, auth_headers):
        resp = client.put("/tasks/9999", json={"title": "Нет"}, headers=auth_headers)
        assert resp.status_code == 404

    def test_update_task_of_other_user_returns_404(self, client, auth_headers, second_user_headers):
        task = client.post("/tasks", json={"title": "Чужая"}, headers=second_user_headers).json()
        resp = client.put(f"/tasks/{task['id']}", json={"title": "Взломано"}, headers=auth_headers)
        assert resp.status_code == 404

    def test_update_task_invalid_priority_returns_422(self, client, auth_headers, created_task):
        resp = client.put(f"/tasks/{created_task['id']}", json={"priority": 10}, headers=auth_headers)
        assert resp.status_code == 422

    def test_update_task_empty_title_returns_422(self, client, auth_headers, created_task):
        resp = client.put(f"/tasks/{created_task['id']}", json={"title": ""}, headers=auth_headers)
        assert resp.status_code == 422


class TestDeleteTask:

    def test_delete_task_returns_204(self, client, auth_headers, created_task):
        resp = client.delete(f"/tasks/{created_task['id']}", headers=auth_headers)
        assert resp.status_code == 204

    def test_delete_task_removes_it(self, client, auth_headers, created_task):
        task_id = created_task["id"]
        client.delete(f"/tasks/{task_id}", headers=auth_headers)
        assert client.get(f"/tasks/{task_id}", headers=auth_headers).status_code == 404

    def test_delete_task_nonexistent_returns_404(self, client, auth_headers):
        assert client.delete("/tasks/9999", headers=auth_headers).status_code == 404

    def test_delete_task_twice_second_is_404(self, client, auth_headers, created_task):
        task_id = created_task["id"]
        client.delete(f"/tasks/{task_id}", headers=auth_headers)
        assert client.delete(f"/tasks/{task_id}", headers=auth_headers).status_code == 404

    def test_delete_task_of_other_user_returns_404(self, client, auth_headers, second_user_headers):
        task = client.post("/tasks", json={"title": "Чужая"}, headers=second_user_headers).json()
        resp = client.delete(f"/tasks/{task['id']}", headers=auth_headers)
        assert resp.status_code == 404
