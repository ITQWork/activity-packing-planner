from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.models import Item

def test_create_item(client: TestClient):
    response = client.post(
        "/items/",
        json={"name": "Flashlight", "unit_weight": 200.0}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Flashlight"
    assert data["unit_weight"] == 200.0

def test_read_items(client: TestClient, session: Session):
    item = Item(name="Compass", unit_weight=50.0)
    session.add(item)
    session.commit()
    
    response = client.get("/items/")
    assert response.status_code == 200
    data = response.json()
    assert any(i["name"] == "Compass" for i in data)
