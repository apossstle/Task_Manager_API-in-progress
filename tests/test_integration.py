
class TestFullTaskLifecycle:
    """Полный жизненный цикл: регистрация → вход → задачи → удаление."""

    def test_full_user_and_task_flow(self, client):
        # 1. Регистрируемся
        reg = client.post("/users/register", json={"email": "user@test.com", "password": "testpass1"})
        assert reg.status_code == 201

        # 2. Логинимся
        login = client.post("/users/login", data={"username": "user@test.com", "password": "testpass1"})
        assert login.status_code == 200
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        # 3. Создаём задачу
        task = client.post("/tasks", json={"title": "Написать тесты", "priority": 3}, headers=headers).json()
        assert task["status"] == "todo"
        assert task["priority"] == 3

        # 4. Берём в работу
        updated = client.put(f"/tasks/{task['id']}", json={"status": "in_progress"}, headers=headers).json()
        assert updated["status"] == "in_progress"

        # 5. Завершаем
        done = client.put(f"/tasks/{task['id']}", json={"status": "done"}, headers=headers).json()
        assert done["status"] == "done"

        # 6. Фильтруем — должна быть в списке done
        done_list = client.get("/tasks?status=done", headers=headers).json()
        assert any(t["id"] == task["id"] for t in done_list)

        # 7. Удаляем
        assert client.delete(f"/tasks/{task['id']}", headers=headers).status_code == 204

        # 8. Убеждаемся, что задача удалена
        assert client.get(f"/tasks/{task['id']}", headers=headers).status_code == 404

    def test_two_users_data_isolation(self, client):
        """Два пользователя не видят задачи друг друга."""
        def make_user_with_task(email, password, task_title):
            client.post("/users/register", json={"email": email, "password": password})
            token = client.post("/users/login", data={"username": email, "password": password}).json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            client.post("/tasks", json={"title": task_title}, headers=headers)
            return headers

        h1 = make_user_with_task("alice@test.com", "alice123", "Задача Алисы")
        h2 = make_user_with_task("bob@test.com", "bobby123", "Задача Боба")

        alice_tasks = client.get("/tasks", headers=h1).json()
        bob_tasks = client.get("/tasks", headers=h2).json()

        assert len(alice_tasks) == 1
        assert alice_tasks[0]["title"] == "Задача Алисы"
        assert len(bob_tasks) == 1
        assert bob_tasks[0]["title"] == "Задача Боба"

    def test_filters_combined(self, client, auth_headers):
        """Комбинированный тест: несколько задач с разными priority/status."""
        client.post("/tasks", json={"title": "Low todo", "priority": 1}, headers=auth_headers)
        t2 = client.post("/tasks", json={"title": "High todo", "priority": 3}, headers=auth_headers).json()
        client.post("/tasks", json={"title": "High done", "priority": 3}, headers=auth_headers)

        # Переводим третью в done
        all_tasks = client.get("/tasks", headers=auth_headers).json()
        high_tasks = [t for t in all_tasks if t["priority"] == 3]
        high_done_id = next(t["id"] for t in high_tasks if t["id"] != t2["id"])
        client.put(f"/tasks/{high_done_id}", json={"status": "done"}, headers=auth_headers)

        # Фильтр: priority=3
        by_priority = client.get("/tasks?priority=3", headers=auth_headers).json()
        assert len(by_priority) == 2

        # Фильтр: status=done
        by_status = client.get("/tasks?status=done", headers=auth_headers).json()
        assert len(by_status) == 1
        assert by_status[0]["priority"] == 3


class TestHealthAndDocs:

    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_docs_available(self, client):
        assert client.get("/docs").status_code == 200

    def test_redoc_available(self, client):
        assert client.get("/redoc").status_code == 200
