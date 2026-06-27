from httpx import AsyncClient

async def test_register_user_success(client: AsyncClient):
    test_user_data = {
        "email": "tester_user1@mail.ru",
        "password": "super_secret_password_example!1@2#3$4%5^6&7*8(9)0",
        "full_name": "User Tester"
    }
    
    response = await client.post("auth/users", json=test_user_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["email"] == test_user_data["email"]
    
    assert "password" not in response_data
    assert "hash_password" not in response_data
    