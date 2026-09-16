rom fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_openapi_schema_available():
    """Проверяем, что приложение поднимается и FastAPI сгенерировал схему."""
    response = client.get("/openapi.json")
    assert response.status_code == 200


def test_app_title():
    """Проверяем, что título приложения совпадает с ожидаемым."""
    assert app.title == "Todo API"
