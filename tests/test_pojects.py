from httpx import AsyncClient
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.project import Project
from app.models.project_member import ProjectMember, Role
from app.models.task import Task
from tests.factories import UserFactory, ProjectFactory, TaskFactory

async def test_create_project_success(client: AsyncClient):
    """Позитивный сценарий: проверка создания проекта авторизованным пользователем."""
    user = await UserFactory.create()
    token = create_access_token({"sub": user.email})
    headers = {"Authorization": f"Bearer {token}"}
    
    project_payload = {
        "title": "Разработка PyTaskAPI",
        "description": "Создание корпоративного менеджера задач"
    }
    response = await client.post("/projects", json=project_payload, headers=headers)
    
    assert response.status_code == 200
    assert response.json()["title"] == project_payload["title"]
        
async def test_create_project_unauthorized_fail(client: AsyncClient):
    """Негативный сценарий: проверка защиты проекта от неавторизованных гостей."""
    
    project_data = {
        "title": "Секретный проект",
        "description": "Сюда нельзя без токена"
    }
    response = await client.post("/projects", json=project_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    
async def test_delete_project_cascade_tasks(client: AsyncClient, db_session: AsyncSession):
    """Проверка целостности БД: при удалении проекта OWNER-ом, удаляются и его задачи."""
    owner = await UserFactory.create()
    project = await ProjectFactory.create()
    db_session.add(ProjectMember(project_id=project.id, user_id=owner.id, role=Role.OWNER))
    task = await TaskFactory.create(project_id=project.id, performer_id=owner.id)
    
    token = create_access_token({"sub": owner.email})
    response = await client.delete(f"/projects/{project.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204
    
    is_project_exists = await db_session.scalar(select(exists().where(Project.id == project.id)))
    is_task_exists = await db_session.scalar(select(exists().where(Task.id == task.id)))

    assert not is_project_exists
    assert not is_task_exists
    