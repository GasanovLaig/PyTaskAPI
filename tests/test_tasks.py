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
    assert bad_result.status_code == 403
    assert bad_result.json()["detail"] == "У вас недостаточно прав для выполнения этого действия в проекте"
    
    # 5. Проверка №2: Владелец проекта добавляет задачу в свой проект -> Ожидаем 200 OK
    good_result = await client.post(
        f"/projects/{project_id}/tasks",
        json=task_payload,
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    assert good_result.status_code == 200
    assert good_result.json()["title"] == task_payload["title"]
    