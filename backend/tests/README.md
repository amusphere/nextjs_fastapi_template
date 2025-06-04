Ø# FastAPI エンドポイントテスト仕様書

## 概要

このドキュメントは、FastAPI + SQLModelバックエンドAPIの包括的なエンドポイントテストスイートについて説明します。すべてのAPIエンドポイントに対する統合的なテストカバレッジを提供します。

## テスト設計原則

### エンドポイント中心設計
- **実際のHTTPリクエスト/レスポンスをテスト**
- **データベース分離による完全なテスト独立性**
- **サービス/リポジトリ層のモッキングなし**
- **実際のアプリケーション動作に近い統合テスト**

### テスト環境設定
- **データベース**: SQLite インメモリ (`sqlite:///:memory:`)
- **認証**: 実際のJWTトークン生成・検証
- **データ分離**: トランザクションベースの完全分離
- **高速実行**: インメモリDBによる高速テスト実行

## テスト構造

テストディレクトリは実際のAPI構造を完全に反映:

```
tests/routers/api/           # API エンドポイントテストのみ
├── test_auth.py            # /api/auth/* 認証エンドポイント
├── test_chat.py            # /api/chat/* チャットエンドポイント
├── test_health.py          # /api/health ヘルスチェック
└── test_users.py           # /api/users/* ユーザー管理
```

**注意**: このディレクトリには**エンドポイントテストのみ**を配置します。ユニットテストやサービス層テストは別の場所で管理されます。

## 完全なテストカバレッジ

**合計**: 29 エンドポイントテスト ✅
**カバレッジ**: 全APIエンドポイント対応
**成功率**: 100% (29/29)

### 認証API (`/api/auth/*`)
**ファイル**: `test_auth.py` | **テスト数**: 15

| エンドポイント | メソッド | テストケース | 状態 |
|---------------|---------|-------------|------|
| `/api/auth/signin` | POST | 有効認証情報、無効メール、無効パスワード | ✅ |
| `/api/auth/signup` | POST | 有効登録、重複メール、無効形式 | ✅ |
| `/api/auth/forgot-password` | POST | 有効メール、存在しないメール、無効形式 | ✅ |
| `/api/auth/change-password` | POST | 有効変更、誤ったパスワード、未認証 | ✅ |

**特殊テスト**:
- パスワードハッシュ化検証
- JWTトークン生成・検証
- 認証フロー統合テスト

### ユーザー管理API (`/api/users/*`)
**ファイル**: `test_users.py` | **テスト数**: 6

| エンドポイント | メソッド | テストケース | 状態 |
|---------------|---------|-------------|------|
| `/api/users/me` | GET | 認証済み取得、未認証アクセス | ✅ |
| `/api/users/me` | PUT | 認証済み更新、未認証更新、無効データ | ✅ |
| `/api/users/create` | POST | エンドポイント存在確認 | ✅ |

### チャットAPI (`/api/chat/*`)
**ファイル**: `test_chat.py` | **テスト数**: 6

| エンドポイント | メソッド | テストケース | 状態 |
|---------------|---------|-------------|------|
| `/api/chat` | POST | 有効プロンプト、空プロンプト、無効JSON、長文、特殊文字 | ✅ |

**バリデーション**:
- Pydantic `min_length=1` 制約
- カスタムバリデーター（空白のみ拒否）
- 境界値テスト（最小有効プロンプト）

### システムAPI (`/api/health`)
**ファイル**: `test_health.py` | **テスト数**: 2

| エンドポイント | メソッド | テストケース | 状態 |
|---------------|---------|-------------|------|
| `/api/health` | GET | 正常性確認、レスポンス形式検証 | ✅ |

## テストアーキテクチャ

### 1. テストデータ管理
**TestUserFactory パターン** - 一貫したテストデータ生成:
```python
# tests/fixtures/test_data.py
class TestUserFactory:
    @staticmethod
    def create_user_data(email: str = None, name: str = None) -> dict:
        return {
            "email": email or TestConstants.TEST_USER_EMAIL,
            "name": name or TestConstants.TEST_USER_NAME,
            "password": TestConstants.TEST_PASSWORD,
        }
```

### 2. データベース完全分離
**トランザクション分離** - テスト間の完全な独立性:
```python
# tests/fixtures/database.py
@pytest.fixture(scope="session")
def test_engine():
    """テスト用SQLiteインメモリエンジン"""

@pytest.fixture
def test_session(test_engine):
    """各テスト用の分離されたセッション（自動ロールバック）"""
```

### 3. 認証済みクライアント
**JWT認証統合** - 実際の認証フローをテスト:
```python
# tests/fixtures/users.py
@pytest.fixture
def authenticated_client(test_client, test_user):
    """JWT認証済みテストクライアント"""
```

### 4. クラスベース構成
**テスト整理** - エンドポイントグループごとの論理的構成:
```python
class TestEmailPasswordAuth:
    """メール/パスワード認証エンドポイント"""

class TestUserProfile:
    """ユーザープロフィール管理エンドポイント"""
```

## 品質保証とベストプラクティス

### 1. テストデータ管理
```python
# ✅ Good: Factoryパターンの使用
user_data = TestUserFactory.create_user_data(email="test@example.com")

# ❌ Avoid: ハードコードされたデータ
user = User(email="test@example.com", password="123")
```

### 2. アサーション品質
```python
# ✅ Good: 具体的で決定論的なアサーション
assert response.status_code == 200
assert "access_token" in response.json()
assert response.json()["email"] == expected_email

# ❌ Avoid: 曖昧なアサーション
assert response.status_code in [200, 422]  # 曖昧すぎる
assert response.json()  # 何を検証しているか不明
```

### 3. テストケース構成
```python
class TestEndpointGroup:
    """エンドポイントグループの包括的テスト"""

    BASE_URL = "/api/endpoint-group"

    def test_endpoint_success_case(self, test_client):
        """正常系: 有効なリクエストで期待される応答"""

    def test_endpoint_validation_error(self, test_client):
        """異常系: 無効なデータでバリデーションエラー"""

    def test_endpoint_authentication_required(self, authenticated_client):
        """認証系: 認証が必要なエンドポイント"""
```

### 4. データベーステスト設計
```python
def test_database_isolation(test_session):
    """データベース分離の確認"""
    # テスト用データ作成
    user = User(email="test@example.com")
    test_session.add(user)
    test_session.commit()

    # データが存在することを確認
    found_user = test_session.get(User, user.id)
    assert found_user is not None

    # テスト終了後、自動的にロールバックされる
```

## 実行方法

### 基本コマンド
```bash
# 全エンドポイントテスト実行
python -m pytest tests/routers/api/ -v

# 特定のエンドポイントグループ
python -m pytest tests/routers/api/test_auth.py -v
python -m pytest tests/routers/api/test_users.py -v
python -m pytest tests/routers/api/test_chat.py -v

# 特定のテストクラス
python -m pytest tests/routers/api/test_auth.py::TestEmailPasswordAuth -v

# カバレッジレポート生成
python -m pytest tests/routers/api/ --cov=app --cov-report=html

# 詳細出力（デバッグ用）
python -m pytest tests/routers/api/ -v -s
```

### パフォーマンス実行
```bash
# 並列実行（pytest-xdist使用）
python -m pytest tests/routers/api/ -n auto

# 最初の失敗で停止
python -m pytest tests/routers/api/ -x

# 失敗したテストのみ再実行
python -m pytest tests/routers/api/ --lf
```

## 新しいエンドポイントテスト追加ガイド

### 1. 新しいAPIルーターの場合
```bash
# 新しいテストファイルを作成
touch tests/routers/api/test_new_endpoint.py
```

### 2. テスト実装テンプレート
```python
# tests/routers/api/test_new_endpoint.py
import pytest
from tests.fixtures.test_data import TestConstants, TestUserFactory

class TestNewEndpointGroup:
    """新しいエンドポイントグループのテスト"""

    BASE_URL = "/api/new-endpoint"

    def test_endpoint_success_case(self, test_client):
        """正常系テスト"""
        response = test_client.get(f"{self.BASE_URL}/path")
        assert response.status_code == 200
        assert "expected_field" in response.json()

    def test_endpoint_error_case(self, test_client):
        """異常系テスト"""
        response = test_client.post(f"{self.BASE_URL}/path", json={})
        assert response.status_code == 422

    def test_authenticated_endpoint(self, authenticated_client):
        """認証が必要なエンドポイント"""
        response = authenticated_client.get(f"{self.BASE_URL}/protected")
        assert response.status_code == 200
```

### 3. ベストプラクティス
- **クラスベース構成**: 関連エンドポイントをクラスでグループ化
- **BASE_URL定数**: エンドポイントベースURLを定数として定義
- **Factory使用**: `TestUserFactory`でテストデータ生成
- **具体的アサーション**: 曖昧な検証を避け、具体的な期待値を設定

## アーキテクチャ

### データベース設定
```python
# tests/fixtures/database.py
@pytest.fixture(scope="session")
def test_engine():
    """テスト用SQLiteインメモリエンジン"""

@pytest.fixture
def test_session(test_engine):
    """各テスト用の分離されたセッション"""
```

### テストクライアント設定
```python
# tests/conftest.py
@pytest.fixture
def test_client(test_session, test_engine):
    """FastAPI テストクライアント"""

@pytest.fixture
def authenticated_client(test_client, authenticated_user):
    """JWT認証済みテストクライアント"""
```

### テストデータファクトリー
```python
# tests/fixtures/test_data.py
class TestUserFactory:
    @staticmethod
    def create_user_data(**kwargs) -> dict:
        """一貫したテストユーザーデータを生成"""
```

## 技術解決事例

### 主要な技術課題と解決策

#### 1. データベースセッション統合問題
**課題**: 認証機能が新しいDBセッションを作成し、テスト用SQLiteデータベースを無視
```python
# 問題のあるコード
def authenticate_user(email: str, password: str):
    session = Session(get_engine())  # テストDBを無視
```

**解決**: 統一されたセッション管理コンテキストマネージャー
```python
# app/utils/database_utils.py
@contextmanager
def get_db_session():
    if is_test_environment():
        session = get_test_session()
    else:
        session = Session(get_engine())
    # ...統一された管理
```

#### 2. テスト間データ分離問題
**課題**: テスト実行順序に依存したデータ汚染
**解決**: ネストしたトランザクションによる完全分離
```python
@pytest.fixture
def test_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()  # 確実なロールバック
    connection.close()
```

#### 3. 曖昧なテストアサーション問題
**課題**: `assert response.status_code in [200, 422]` のような決定論的でない検証
**解決**: Pydanticバリデーションとの組み合わせで具体的な期待値設定
```python
# モデル強化
class ChatRequestModel(BaseModel):
    prompt: str = Field(min_length=1)

    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('プロンプトは空白のみにできません')
        return v

# 具体的なテスト
def test_empty_prompt_validation_error(self, test_client):
    response = test_client.post("/api/chat", json={"prompt": ""})
    assert response.status_code == 422
    assert "min_length" in response.json()["detail"][0]["type"]
```

## トラブルシューティング

### よくある問題と解決法

#### 1. "no such table" エラー
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: user
```
**原因**: SQLModelメタデータが適切に設定されていない
**解決**: スキーマインポートを確認
```python
# tests/fixtures/database.py
from app.models.user import User  # 必須インポート
from app.models.password import PasswordResetToken
```

#### 2. "Multiple rows found" エラー
```
sqlalchemy.exc.MultipleResultsFound: Multiple rows were found when exactly one was expected
```
**原因**: テスト間でデータが分離されていない
**解決**: トランザクションロールバックを確認

#### 3. 認証テスト失敗
```
AssertionError: assert 500 == 200
```
**原因**: テスト用DBセッションが使用されていない
**解決**: 依存性注入の設定を確認

### デバッグ用ユーティリティ

```python
# データベース状態確認
def debug_database_state(test_session):
    """テスト中のデータベース状態を確認"""
    users = test_session.exec(select(User)).all()
    print(f"Current users: {len(users)}")
    for user in users:
        print(f"  {user.id}: {user.email}")

# テスト用
def test_debug_example(test_session):
    debug_database_state(test_session)
    # テストコード
```

## まとめ

このテストスイートは以下を達成しています：

✅ **完全なエンドポイントカバレッジ**: 29テストで全APIエンドポイントをカバー
✅ **実際の統合テスト**: モッキングなしの実際の動作テスト
✅ **データ分離**: 各テストが独立したデータベース状態を持つ
✅ **高品質アサーション**: 具体的で決定論的なテスト検証
✅ **保守性**: クラスベース構成とファクトリーパターンで保守しやすい構造

**重要な成果**:
- 元の失敗していた認証テスト(`test_get_current_user_authenticated`)を完全に修正
- SQLite `:memory:` データベースでの完全な分離を実現
- テスト構造をAPI構造と完全に一致させ、保守性を大幅に向上

このテストスイートにより、APIの信頼性とコードの品質が大幅に向上し、継続的な開発とデプロイメントが安全に行えるようになりました。
