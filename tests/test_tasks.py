import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_member import ProjectMember, Role
from tests.factories import ProjectFactory, UserFactory, TaskFactory

@pytest.mark.asyncio
async def test_get_task_by_id_success(client: AsyncClient, db_session: AsyncSession):
    """Тест успешного чтения задачи участником проекта (Чистый Happy Path)."""
    user = await UserFactory.create()
    project = await ProjectFactory.create()
    task = await TaskFactory.create(project=project, performer=user)
    
    db_session.add(ProjectMember(user_id=user.id, project_id=project.id, role=Role.DEVELOPER))
    await db_session.flush()
    
    from app.core.security import create_access_token
    token = create_access_token({"sub": user.email})
    response = await client.get(
        f"/projects/{project.id}/tasks/{task.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["title"] == task.title
    

async def test_create_task_owner_success(client: AsyncClient):
    """ТЕСТ 1: Проверяем позитивный сценарий (Владелец может создать задачу)"""
    
    # 1. Регистрируем и логиним Владельца
    user_payload = {"email": "owner@mail.ru", "password": "pwd_example_!1", "full_name": "Owner Tester"}
    await client.post("/auth/users", json=user_payload)
    login = await client.post("/auth/login", data={"username": user_payload["email"], "password": user_payload["password"]})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Создаем проект
    project_payload = {"title": "Проект Владельца", "description": "Описание"}
    project_result = await client.post("/projects", json=project_payload, headers=headers)
    project_id = project_result.json()["id"]

    # 3. Создаем задачу -> Ожидаем 200 OK
    task_payload = {"title": "Задача владельца", "description": "Детали"}
    good_result = await client.post(f"/projects/{project_id}/tasks", json=task_payload, headers=headers)
    
    assert good_result.status_code == 200
    assert good_result.json()["title"] == task_payload["title"]
    
async def test_create_task_stranger_forbidden_fail(client: AsyncClient):
    """ТЕСТ 2: Проверяем негативный сценарий (Чужак получает 404)"""
    
    # 1. Логиним Владельца и создаем проект
    user1_payload = {"email": "owner2@mail.ru", "password": "pwd_example_!1", "full_name": "Owner"}
    await client.post("/auth/users", json=user1_payload)
    login1 = await client.post("/auth/login", data={"username": user1_payload["email"], "password": user1_payload["password"]})
    owner_token = login1.json()["access_token"]
    
    project_result = await client.post(
        "/projects", 
        json={"title": "Секретный проект", "description": ""}, 
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    project_id = project_result.json()["id"]

    # 2. Логиним Чужака
    user2_payload = {"email": "stranger2@mail.ru", "password": "pwd_example_@2", "full_name": "Stranger"}
    await client.post("/auth/users", json=user2_payload)
    login2 = await client.post("/auth/login", data={"username": user2_payload["email"], "password": user2_payload["password"]})
    stranger_token = login2.json()["access_token"]

    # 3. Чужак стучится в проект -> Ожидаем 404
    task_payload = {"title": "Взлом задачи", "description": ""}
    bad_result = await client.post(
        f"/projects/{project_id}/tasks", 
        json=task_payload, 
        headers={"Authorization": f"Bearer {stranger_token}"}
    )
    assert bad_result.status_code == 404
    
async def test_update_task_flow_success(client: AsyncClient):
    """Тестирование изменения статуса задачи и смены исполнителя (PATCH)."""
    
    user_payload = {"email": "manager@test.ru", "password": "pwd_example_!1", "full_name": "User Tester"}
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
    user_payload = {"email": "tree_tester@test.ru", "password": "pwd_example_@2", "full_name": "Tree Tester"}
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
    