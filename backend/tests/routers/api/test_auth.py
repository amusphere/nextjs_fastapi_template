"""Auth API endpoint tests."""

from tests.fixtures.test_data import TestConstants


class TestEmailPasswordAuth:
    """Email/Password認証のテスト"""

    BASE_URL = TestConstants.AUTH_BASE

    def test_signin_valid_credentials(self, test_client, test_user):
        """有効な認証情報でのサインインテスト"""
        login_data = {
            "username": test_user.email,  # OAuth2PasswordRequestFormはusernameフィールドを使用
            "password": "test_password_123",  # test_data.pyで定義したデフォルトパスワード
        }

        response = test_client.post(
            f"{self.BASE_URL}/signin",
            data=login_data,  # form-dataとして送信
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_signin_invalid_email(self, test_client):
        """無効なメールアドレスでのサインインテスト"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "test_password_123",
        }

        response = test_client.post(
            f"{self.BASE_URL}/signin",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_signin_invalid_password(self, test_client, test_user):
        """無効なパスワードでのサインインテスト"""
        login_data = {"username": test_user.email, "password": "wrong_password"}

        response = test_client.post(
            f"{self.BASE_URL}/signin",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]


class TestAuthUtilities:
    """認証ユーティリティのテスト"""

    def test_password_hashing(self):
        """パスワードハッシュ化のテスト"""
        from app.utils.auth.email_password import get_password_hash, verify_password

        password = "test_password_123"
        hashed = get_password_hash(password)

        # ハッシュが元のパスワードと異なることを確認
        assert hashed != password

        # ハッシュの検証が正しく動作することを確認
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False

    def test_jwt_token_creation_and_validation(self, authenticated_user):
        """JWTトークンの作成と検証のテスト"""
        from datetime import timedelta

        from app.utils.auth.email_password import create_access_token, create_sub

        # トークン作成
        token_data = create_sub(authenticated_user)
        access_token = create_access_token(
            data=token_data, expires_delta=timedelta(minutes=30)
        )

        # トークンが文字列であることを確認
        assert isinstance(access_token, str)
        assert len(access_token) > 0


class TestUserRegistration:
    """ユーザー登録のテスト"""

    BASE_URL = TestConstants.AUTH_BASE

    def test_signup_valid_data(self, test_client):
        """有効なデータでのユーザー登録"""
        signup_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "strong_password_123",
        }

        response = test_client.post(f"{self.BASE_URL}/signup", json=signup_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_signup_duplicate_email(self, test_client, test_user):
        """既存のメールアドレスでのユーザー登録"""
        signup_data = {
            "username": "duplicateuser",
            "email": test_user.email,  # 既存のメール
            "password": "password_123",
        }

        response = test_client.post(f"{self.BASE_URL}/signup", json=signup_data)

        assert response.status_code == 400

    def test_signup_invalid_email_format(self, test_client):
        """不正なメール形式でのユーザー登録"""
        signup_data = {
            "email": "invalid-email",
            "password": "password_123",
            "name": "Test User",
        }

        response = test_client.post(f"{self.BASE_URL}/signup", json=signup_data)

        assert response.status_code == 422


class TestPasswordReset:
    """パスワードリセット機能のテスト"""

    BASE_URL = TestConstants.AUTH_BASE

    def test_forgot_password_valid_email(self, test_client, test_user):
        """有効なメールアドレスでのパスワードリセット要求"""
        response = test_client.post(
            f"{self.BASE_URL}/forgot-password",
            json={"email": test_user.email},
        )

        assert response.status_code == 200
        assert "message" in response.json()
        assert "reset link" in response.json()["message"].lower()

    def test_forgot_password_nonexistent_email(self, test_client):
        """存在しないメールアドレスでのパスワードリセット要求"""
        response = test_client.post(
            f"{self.BASE_URL}/forgot-password",
            json={"email": "nonexistent@example.com"},
        )

        # セキュリティ上、存在しないメールでも200を返す
        assert response.status_code == 200
        assert "message" in response.json()

    def test_forgot_password_invalid_email_format(self, test_client):
        """不正な形式のメールアドレスでのパスワードリセット要求"""
        response = test_client.post(
            f"{self.BASE_URL}/forgot-password",
            json={"email": "invalid-email"},
        )

        # セキュリティ上の理由で、無効なメールでも成功レスポンスを返す
        assert response.status_code == 200
        assert response.json() == {
            "message": "If the email exists, a reset link was sent."
        }

    def test_change_password_authenticated_user(self, authenticated_client):
        """認証済みユーザーのパスワード変更"""
        change_data = {
            "current_password": "test_password_123",
            "new_password": "new_password_456",
        }

        response = authenticated_client.post(
            f"{self.BASE_URL}/change-password",
            json=change_data,
        )

        assert response.status_code == 200
        assert "message" in response.json()
        assert "changed" in response.json()["message"].lower()

    def test_change_password_wrong_current_password(self, authenticated_client):
        """間違った現在のパスワードでの変更試行"""
        change_data = {
            "current_password": "wrong_password",
            "new_password": "new_password_456",
        }

        response = authenticated_client.post(
            f"{self.BASE_URL}/change-password",
            json=change_data,
        )

        assert response.status_code == 400
        assert "Current password is incorrect" in response.json()["detail"]

    def test_change_password_unauthenticated(self, test_client):
        """認証されていないユーザーのパスワード変更試行"""
        change_data = {
            "current_password": "test_password_123",
            "new_password": "new_password_456",
        }

        response = test_client.post(
            f"{self.BASE_URL}/change-password",
            json=change_data,
        )

        assert response.status_code == 401
