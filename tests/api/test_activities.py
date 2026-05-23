from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.models import Activity, Item, ActivityItemLink

def test_create_activity(client: TestClient):
    response = client.post(
        "/activities/",
        json={"name": "Running"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Running"
    assert "id" in data

def test_read_activities(client: TestClient, session: Session):
    activity = Activity(name="Swimming")
    session.add(activity)
    session.commit()
    
    response = client.get("/activities/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(a["name"] == "Swimming" for a in data)

def test_add_item_to_activity(client: TestClient, session: Session):
    activity = Activity(name="Cycling")
    item = Item(name="Helmet", unit_weight=500)
    session.add(activity)
    session.add(item)
    session.commit()
    
    response = client.post(
        f"/activities/{activity.id}/items/{item.id}?base_quantity=1"
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Item added/updated in activity"}

def test_delete_activity(client: TestClient, session: Session):
    activity = Activity(name="Skydiving")
    session.add(activity)
    session.commit()
    
    response = client.delete(f"/activities/{activity.id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Activity deleted"}
