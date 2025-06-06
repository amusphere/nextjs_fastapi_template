"""Health endpoint tests."""


def test_health_check(test_client):
    """ヘルスチェックエンドポイントのテスト"""
    response = test_client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
