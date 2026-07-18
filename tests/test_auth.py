from httpx import AsyncClient

async def test_register_user_success(client: AsyncClient):
    test_user_data = {
        "email": "user@test.ru",
        "password": "pwd_example!1@2#3",
        "full_name": "User Full Name"
    }
    
    response = await client.post("/auth/users", json=test_user_data)
    assert response.status_code == 200
    
    response_data = response.json()
    assert response_data["email"] == test_user_data["email"]
    
    assert "password" not in response_data
    assert "hash_password" not in response_data
    
async def test_register_user_duplicate_email_fail(client: AsyncClient):
    test_user_data = {
        "email": "duplicate_user@test.ru",
        "password": "pwd_example*8(9)0",
        "full_name": "Duplicate User Full Name"
    }
    
    first_response = await client.post("/auth/users", json=test_user_data)
    assert first_response.status_code == 200
    
    second_response = await client.post("/auth/users", json=test_user_data)
    assert second_response.status_code == 409
    
    response_data = second_response.json()
    assert response_data["detail"] == "Запись с таким уникальными данными уже существует"
    