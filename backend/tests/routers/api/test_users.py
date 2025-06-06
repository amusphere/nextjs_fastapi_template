"""Users API endpoint tests."""

from tests.fixtures.test_data import TestConstants


class TestUsersEndpoints:
    """ユーザーAPI エンドポイントのテスト"""

    BASE_URL = TestConstants.USERS_BASE

    def test_get_current_user_unauthenticated(self, test_client):
        """認証されていない場合のテスト"""
        url = f"{self.BASE_URL}/me"
        response = test_client.get(url)
        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    def test_get_current_user_authenticated(self, authenticated_client, authenticated_user):
        """認証済みユーザーがプロフィールを取得できることをテスト"""
        url = f"{self.BASE_URL}/me"
        response = authenticated_client.get(url)
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["email"] == authenticated_user.email
        assert user_data["name"] == authenticated_user.name
        assert user_data["uuid"] == str(authenticated_user.uuid)

    def test_update_current_user_authenticated(self, authenticated_client, authenticated_user):
        """認証済みユーザーがプロフィールを更新できることをテスト"""
        update_data = {
            "name": "Updated Name",
        }

        response = authenticated_client.put(
            f"{self.BASE_URL}/me",
            json=update_data
        )

        assert response.status_code == 200
        user_data = response.json()
        assert user_data["name"] == "Updated Name"
        assert user_data["email"] == authenticated_user.email  # 変更されない

    def test_update_current_user_unauthenticated(self, test_client):
        """認証されていないユーザーのプロフィール更新試行"""
        update_data = {
            "name": "Should Not Update",
        }

        response = test_client.put(
            f"{self.BASE_URL}/me",
            json=update_data
        )

        assert response.status_code == 401

    def test_update_current_user_invalid_data(self, authenticated_client):
        """不正なデータでのプロフィール更新"""
        # 不正なデータ型
        update_data = {
            "name": 123,  # 文字列であるべき
        }

        response = authenticated_client.put(
            f"{self.BASE_URL}/me",
            json=update_data
        )

        assert response.status_code == 422

    def test_create_user_endpoint_exists(self, test_client):
        """ユーザー作成エンドポイントの存在確認"""
        # このエンドポイントはClerk用だが、存在することを確認
        response = test_client.post(f"{self.BASE_URL}/create")

        # AUTH_SYSTEM=email_passwordの場合は400が期待される
        # 認証されていない場合は401が期待される
        assert response.status_code in [400, 401]


# 後方互換性のための関数ベースのテスト
def test_get_current_user_unauthenticated(test_client):
    """認証されていない場合のテスト（後方互換性）"""
    BASE_URL = "/api/users"
    url = f"{BASE_URL}/me"
    response = test_client.get(url)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_get_current_user_authenticated(authenticated_client, authenticated_user):
    """認証済みユーザーがプロフィールを取得できることをテスト（後方互換性）"""
    BASE_URL = "/api/users"
    url = f"{BASE_URL}/me"
    response = authenticated_client.get(url)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == authenticated_user.email
    assert user_data["name"] == authenticated_user.name
    assert user_data["uuid"] == str(authenticated_user.uuid)
