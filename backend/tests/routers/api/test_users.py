from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

base_url = "/api/users"


def test_get_current_user_unauthenticated(test_client):
    """認証されていない場合のテスト"""
    url = f"{base_url}/me"
    response = test_client.get(url)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_get_current_user_authenticated(authenticated_client, authenticated_user):
    """認証済みユーザーがプロフィールを取得できることをテスト"""
    url = f"{base_url}/me"
    response = authenticated_client.get(url)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == authenticated_user.email
    assert user_data["name"] == authenticated_user.name
    assert user_data["uuid"] == str(authenticated_user.uuid)
