from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.project_member import ProjectMember, Role
from tests.factories import ProjectFactory, UserFactory, TaskFactory

async def test_get_task_by_id_success(client: AsyncClient, db_session: AsyncSession):
    """Позитивный сценарий: чтение задачи участником проекта."""
    user = await UserFactory.create()
    project = await ProjectFactory.create()
    db_session.add(ProjectMember(user_id=user.id, project_id=project.id, role=Role.DEVELOPER))
    task = await TaskFactory.create(project_id=project.id, performer_id=user.id)
    
    token = create_access_token({"sub": user.email})
    response = await client.get(
        f"/projects/{project.id}/tasks/{task.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["title"] == task.title

async def test_create_task_owner_success(client: AsyncClient, db_session: AsyncSession):
    """Позитивный сценарий: OWNER проекта может создавать задачи."""
    owner = await UserFactory.create()
    project = await ProjectFactory.create()
    db_session.add(ProjectMember(user_id=owner.id, project_id=project.id, role=Role.OWNER))
    await db_session.flush()
    token = create_access_token({"sub": owner.email})
    task_payload = {"title": "Название задачи", "description": ""}
    
    response = await client.post(
        f"/projects/{project.id}/tasks",
        json=task_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["title"] == task_payload["title"]
    
async def test_create_task_stranger_forbidden_fail(client: AsyncClient, db_session: AsyncSession):
    """Негативный сценарий: чужак получает 404 при попытке создать задачу в чужом проекте."""
    owner = await UserFactory.create()
    owner_project = await ProjectFactory.create()
    db_session.add(ProjectMember(user_id=owner.id, project_id=owner_project.id, role=Role.OWNER))
    await db_session.flush()
    
    stranger = await UserFactory.create()
    stranger_token = create_access_token({"sub": stranger.email})
    
    task_payload = {"title": "Название задачи", "description": ""}
    response = await client.post(
        f"/projects/{owner_project.id}/tasks",
        json=task_payload,
        headers={"Authorization": f"Bearer {stranger_token}"}
    )
    
    assert response.status_code == 404
    
async def test_update_task_flow_success(client: AsyncClient, db_session: AsyncSession):
    """Позитивный сценарий: проверка обновления задачи."""
    user = await UserFactory.create()
    project = await ProjectFactory.create()
    db_session.add(ProjectMember(user_id=user.id, project_id=project.id, role=Role.OWNER))
    task = await TaskFactory.create(project_id=project.id, performer_id=user.id)
    token = create_access_token({"sub": user.email})
    
    task_payload = {"title": "Обновленное название задачи", "status": "in_progress"}
    response = await client.patch(
        f"/projects/{project.id}/tasks/{task.id}",
        json=task_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["title"] == task_payload["title"]
    
async def test_get_tasks_tree_structure(client: AsyncClient, db_session: AsyncSession):
    """Позитивный сценарий: проверка древовидной структуры полученнего списка задач."""
    user = await UserFactory.create()
    project = await ProjectFactory.create()
    db_session.add(ProjectMember(project_id=project.id, user_id=user.id, role=Role.DEVELOPER))
    parent_task = await TaskFactory.create(project_id=project.id, performer_id=user.id)
    child_task = await TaskFactory.create(
        project_id=project.id,
        performer_id=user.id,
        parent_task_id=parent_task.id
    )
    
    token = create_access_token({"sub": user.email})
    response = await client.get(
        f"/projects/{project.id}/tasks/tree",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    tree_data = response.json()
    assert len(tree_data) > 0
    assert tree_data[0]["id"] == parent_task.id
    assert tree_data[0]["subtasks"][0]["id"] == child_task.id
    