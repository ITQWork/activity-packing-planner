from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.models import Trip, Activity
from datetime import date

def test_create_trip(client: TestClient, session: Session):
    activity = Activity(name="Camping")
    session.add(activity)
    session.commit()
    
    response = client.post(
        "/trips/",
        json={
            "destination": "Forest",
            "start_date": "2023-06-01",
            "end_date": "2023-06-05",
            "activity_id": activity.id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["destination"] == "Forest"
    assert data["activity_id"] == activity.id

def test_read_trips(client: TestClient, session: Session):
    activity = Activity(name="Beach")
    session.add(activity)
    session.commit()
    
    trip = Trip(
        destination="Coast",
        start_date=date(2023, 7, 1),
        end_date=date(2023, 7, 3),
        activity_id=activity.id
    )
    session.add(trip)
    session.commit()
    
    response = client.get("/trips/")
    assert response.status_code == 200
    data = response.json()
    assert any(t["destination"] == "Coast" for t in data)
