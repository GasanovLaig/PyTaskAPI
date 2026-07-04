from httpx import AsyncClient

async def test_create_task_rbac_flow(client: AsyncClient):
    # "Сценарий проверки прав доступа (RBAC): создание задач разрешено только участникам"
    # 1. Регистрируем и логиним Юзера №1 (Владелец проекта)
    user1_payload = {
        "email": "owner@mail.ru",
        "password": "pwd_example_!1",
        "full_name": "Owner Tester"
    }
    await client.post("/auth/users", json=user1_payload)
    login1 = await client.post(
        "/auth/login",
        data={
            "username": user1_payload["email"],
            "password": user1_payload["password"]
        }
    )
    owner_token = login1.json()["access_token"]
    
    # 2. Регистрируем и логиним Юзера №2 (Чужак, не состоящий в проекте)
    user2_payload = {
        "email": "stranger@mail.ru",
        "password": "pwd_example_@2",
        "full_name": "Stranger Tester"
    }
    await client.post("/auth/users", json=user2_payload)
    login2 = await client.post(
        "/auth/login",
        data={
            "username": user2_payload["email"],
            "password": user2_payload["password"]
        }
    )
    stranger_token = login2.json()["access_token"]
    
    # 3. Юзер №1 создает проект и получает его project_id
    project_payload = {
        "title": "Безопасный проект",
        "description": "Проверяем права доступа"
    }
    project_result = await client.post("/projects", json=project_payload, headers={"Authorization": f"Bearer {owner_token}"})
    project_id = project_result.json()["id"]
    
    task_payload = {
        "title": "Написать тесты безопасности",
        "description": "Проверить перехват 403 ошибки"
    }
    bad_result = await client.post(
        f"/projects/{project_id}/tasks",
        json=task_payload,
        headers={"Authorization": f"Bearer {stranger_token}"}
    )
    assert bad_result.status_code == 404
    assert bad_result.json()["detail"] == "Проект не найден или у вас нет к нему доступа"
    
    # 5. Проверка №2: Владелец проекта добавляет задачу в свой проект -> Ожидаем 200 OK
    good_result = await client.post(
        f"/projects/{project_id}/tasks",
        json=task_payload,
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    assert good_result.status_code == 200
    assert good_result.json()["title"] == task_payload["title"]
    
async def test_update_task_flow_success(client: AsyncClient):
    # "Тестирование изменения статуса задачи и смены исполнителя (PATCH)."
    
    user_payload = {"email": "manager@mail.ru", "password": "pwd_example_!1", "full_name": "User Tester"}
    await client.post("/auth/users", json=user_payload)
    login_result = await client.post("/auth/login", data={"username": user_payload["email"], "password": user_payload["password"]})
    token = login_result.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    project_result = await client.post("/projects", json={"title": "Тест Patch", "description": ""}, headers=headers)
    project_id = project_result.json()["id"]
    
    task_result = await client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Родительская задача"},
        headers=headers
    )
    task_id = task_result.json()["id"]
    assert task_result.json()["status"] == "todo"
    
    update_payload = {
        "title": "Обновленная задача",
        "status": "in_progress"
    }
    patch_result = await client.patch(
        f"/projects/{project_id}/tasks/{task_id}",
        json=update_payload,
        headers=headers
    )
    
    assert patch_result.status_code == 200
    update_data = patch_result.json()
    assert update_data["title"] == "Обновленная задача"
    assert update_data["status"] == "in_progress"
    
async def test_get_tasks_tree_structure(client: AsyncClient):
    user_payload = {"email": "tree_tester@mail.ru", "password": "pwd_example_@2", "full_name": "Tree Tester"}
    await client.post("/auth/users", json=user_payload)
    login_result = await client.post("/auth/login", data={"username": user_payload["email"], "password": user_payload["password"]})
    headers = {"Authorization": f"Bearer {login_result.json()["access_token"]}"}
    
    project_result = await client.post("/projects", json={"title": "Проект для дерева", "description": ""}, headers=headers)
    project_id = project_result.json()["id"]
    
    parent_task_result = await client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Родительская задача"},
        headers=headers
    )
    parent_task_id = parent_task_result.json()["id"]
    
    subtask_result = await client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Дочерняя подзадача", "parent_task_id": parent_task_id},
        headers=headers
    )
    
    tree_result = await client.get(f"/projects/{project_id}/tasks/tree", headers=headers)
    assert tree_result.status_code == 200
    
    tree_data = tree_result.json()
    
    assert len(tree_data) == 1
    root_task = tree_data[0]
    assert root_task["id"] == parent_task_id
    
    assert len(root_task["subtasks"]) == 1
    assert root_task["subtasks"][0]["id"] == subtask_result.json()["id"]
    assert root_task["subtasks"][0]["parent_task_id"] == parent_task_id
    