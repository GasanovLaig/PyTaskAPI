from httpx import AsyncClient

async def test_create_project_full_flow_success(client: AsyncClient):
    # "Сценарий: регистрация -> логин -> получение JWT -> создание проекта."
    
    # Шаг 1: Регистрируем тестового пользователя
    user_data = {
        "email": "project_owner@test.ru",
        "password": "pwd_example!1@2#3",
        "full_name": "User Full Name"
    }
    register_response = await client.post("/auth/users", json=user_data)
    assert register_response.status_code == 200
    
    # Шаг 2: Имитируем вход через OAuth2 форму (передаем данные как form-data, а не JSON!)
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    login_response = await client.post("/auth/login", data=login_data)
    assert login_response.status_code == 200
    
    tokens_json = login_response.json()
    assert "access_token" in tokens_json
    assert tokens_json["token_type"] == "bearer"
    token = tokens_json["access_token"]
    
    # Шаг 3: Формируем заголовки авторизации с полученным JWT-токеном
    headers = {"Authorization": f"Bearer {token}"}
    # Шаг 4: Делаем защищенный запрос на создание проекта
    project_payload = {
        "title": "Разработка PyTaskAPI",
        "description": "Создание корпоративного менеджера задач на FastAPI"
    }
    project_response = await client.post("/projects", json=project_payload, headers=headers)
    
    assert project_response.status_code == 200
    project_data = project_response.json()
    assert project_data["title"] == project_payload["title"]
    assert "id" in project_data
    
async def test_create_project_unauthorized_fail(client: AsyncClient):
    # "Негативный сценарий: проверка защиты проекта от неавторизованных гостей."
    
    project_data = {
        "title": "Секретный проект",
        "description": "Сюда нельзя без токена"
    }
    response = await client.post("/projects", json=project_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"    
    