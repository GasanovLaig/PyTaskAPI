from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_access_token
from app.models.project_member import ProjectMember, Role
from app.models.tag import Tag
from tests.factories import UserFactory, ProjectFactory, TaskFactory

async def test_attach_tag_to_task_success(client: AsyncClient, db_session: AsyncSession):
    """Позитивный сценарий: менеджер успешно привязывает тег к задаче."""
    manager = await UserFactory.create()
    project = await ProjectFactory.create()
    db_session.add(ProjectMember(project_id=project.id, user_id=manager.id, role=Role.MANAGER))
    task = await TaskFactory.create(project_id=project.id, performer_id=manager.id)
    
    tag = Tag(project_id=project.id, name="backend")
    db_session.add(tag)
    await db_session.flush()
    
    token = create_access_token({"sub": manager.email})
    response = await client.put(
        f"/projects/{project.id}/tasks/{task.id}/tags/{tag.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 204
