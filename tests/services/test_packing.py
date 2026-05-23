from datetime import date
from app.services.packing import calculate_duration, generate_trip_packing_list, calculate_trip_weight
from app.models.models import Trip, Activity, Item, ActivityItemLink, TripPackedItem
from sqlmodel import Session, select

def test_calculate_duration():
    start = date(2023, 1, 1)
    end = date(2023, 1, 5)
    assert calculate_duration(start, end) == 5
    
    start = date(2023, 1, 1)
    end = date(2023, 1, 1)
    assert calculate_duration(start, end) == 1

def test_generate_trip_packing_list(session: Session):
    # Setup
    activity = Activity(name="Hiking")
    session.add(activity)
    session.commit()
    
    item1 = Item(name="Boots", unit_weight=1000)
    item2 = Item(name="Water", unit_weight=500)
    session.add(item1)
    session.add(item2)
    session.commit()
    
    link1 = ActivityItemLink(activity_id=activity.id, item_id=item1.id, base_quantity=1)
    link2 = ActivityItemLink(activity_id=activity.id, item_id=item2.id, base_quantity=2)
    session.add(link1)
    session.add(link2)
    session.commit()
    
    trip = Trip(
        destination="Mountains",
        start_date=date(2023, 1, 1),
        end_date=date(2023, 1, 3), # 3 days
        activity_id=activity.id
    )
    session.add(trip)
    session.commit()
    
    # Execute
    generate_trip_packing_list(session, trip)
    
    # Verify
    packed_items = session.exec(select(TripPackedItem).where(TripPackedItem.trip_id == trip.id)).all()
    assert len(packed_items) == 2
    
    boots = next(pi for pi in packed_items if pi.item_id == item1.id)
    water = next(pi for pi in packed_items if pi.item_id == item2.id)
    
    assert boots.quantity == 1 * 3
    assert water.quantity == 2 * 3

def test_calculate_trip_weight(session: Session):
    # Setup
    item1 = Item(name="Boots", unit_weight=1000)
    item2 = Item(name="Water", unit_weight=500)
    session.add(item1)
    session.add(item2)
    session.commit()
    
    trip = Trip(
        destination="Mountains",
        start_date=date(2023, 1, 1),
        end_date=date(2023, 1, 1),
        activity_id=1
    )
    session.add(trip)
    session.commit()
    
    pi1 = TripPackedItem(trip_id=trip.id, item_id=item1.id, quantity=1)
    pi2 = TripPackedItem(trip_id=trip.id, item_id=item2.id, quantity=2)
    session.add(pi1)
    session.add(pi2)
    session.commit()
    
    # Execute
    weight = calculate_trip_weight(session, trip.id)
    
    # Verify
    assert weight == (1000 * 1) + (500 * 2)
