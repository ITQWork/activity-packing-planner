from sqlmodel import Session, select
from models import Trip, TripPackedItem, ActivityItemLink, Activity, Item
from datetime import date

def calculate_duration(start_date: date, end_date: date) -> int:
    duration = (end_date - start_date).days + 1
    return max(1, duration)

def generate_trip_packing_list(session: Session, trip: Trip):
    duration = calculate_duration(trip.start_date, trip.end_date)
    
    # Get all items for the activity
    statement = select(ActivityItemLink).where(ActivityItemLink.activity_id == trip.activity_id)
    links = session.exec(statement).all()
    
    for link in links:
        quantity = link.base_quantity * duration
        packed_item = TripPackedItem(
            trip_id=trip.id,
            item_id=link.item_id,
            quantity=quantity,
            is_packed=False
        )
        session.add(packed_item)
    session.commit()

def calculate_trip_weight(session: Session, trip_id: int) -> float:
    statement = select(TripPackedItem).where(TripPackedItem.trip_id == trip_id)
    packed_items = session.exec(statement).all()
    
    total_weight = 0.0
    for pi in packed_items:
        item = session.get(Item, pi.item_id)
        if item:
            total_weight += item.unit_weight * pi.quantity
    return total_weight
