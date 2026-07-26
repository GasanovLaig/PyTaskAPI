from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_access_token
from app.models.project_member import ProjectMember, Role
from tests.factories import UserFactory, ProjectFactory, TaskFactory

async def test_comment_lifecycle_and_rbac(client: AsyncClient, db_session: AsyncSession):
    """Бизнес-сценарий: Участник создает комментарий к задаче, а чужак не может его удалить."""
    # 1. Предусловие: Создаем проект, задачу и автора комментария
    author = await UserFactory.create()
    project = await ProjectFactory.create()
    db_session.add(ProjectMember(project_id=project.id, user_id=author.id, role=Role.DEVELOPER))
    task = await TaskFactory.create(project_id=project.id, performer_id=author.id)
    
    # 2. Действие: Автор пишет комментарий через API
    author_token = create_access_token({"sub": author.email})
    comment_payload = {"text": "Важное уточнение по архитектуре тестов"}
    response = await client.post(
        f"projects/{project.id}/tasks/{task.id}/comments",
        json=comment_payload,
        headers={"Authorization": f"Bearer {author_token}"}
    )
    
    assert response.status_code == 200
    comment_id = response.json()["id"]
    
    # 3. Негативный сценарий (RBAC): Создаем чужака, который пытается удалить этот комментарий
    stranger = await UserFactory.create()
    stranger_token = create_access_token({"sub": stranger.email})
    delete_response = await client.delete(
        f"/projects/{project.id}/tasks/{task.id}/comments/{comment_id}",
        headers={"Authorization": f"Bearer {stranger_token}"}
    )
    
    assert delete_response.status_code in [403, 404]
