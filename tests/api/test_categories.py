from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.models import Category, Item

def test_create_category(client: TestClient):
    response = client.post(
        "/categories/",
        json={"name": "Electronics"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Electronics"

def test_read_categories(client: TestClient, session: Session):
    category = Category(name="Clothing")
    session.add(category)
    session.commit()
    
    response = client.get("/categories/")
    assert response.status_code == 200
    data = response.json()
    assert any(c["name"] == "Clothing" for c in data)
