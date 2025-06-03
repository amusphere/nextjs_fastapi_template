from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

base_url = "/api/users"


def test_get_current_user():
    url = f"{base_url}/me"
    response = client.get(url)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
