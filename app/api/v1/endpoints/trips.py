from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from app.db.session import get_session
from app.models.models import Trip, TripPackedItem, Reminder, Item as ItemModel, Category
from app.schemas.schemas import Trip as TripSchema, TripCreate, TripUpdate, TripPackedItem as TripPackedItemSchema, Message
from app.services.packing import generate_trip_packing_list, calculate_trip_weight
from app.services.weather import get_weather_forecast
from app.services.pdf import generate_pdf

router = APIRouter()

@router.post("/", response_model=TripSchema)
def create_trip(trip_in: TripCreate, session: Session = Depends(get_session)):
    trip = Trip.from_orm(trip_in)
    session.add(trip)
    session.commit()
    session.refresh(trip)
    
    # Generate packing list
    generate_trip_packing_list(session, trip)
    
    return trip

@router.get("/", response_model=List[TripSchema])
def read_trips(user_id: Optional[int] = None, session: Session = Depends(get_session)):
    query = select(Trip)
    if user_id:
        query = query.where(Trip.user_id == user_id)
    return session.exec(query).all()

@router.delete("/{trip_id}", response_model=Message)
def delete_trip(trip_id: int, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Delete packed items
    packed_items = session.exec(select(TripPackedItem).where(TripPackedItem.trip_id == trip_id)).all()
    for item in packed_items:
        session.delete(item)
    
    # Delete reminders
    reminders = session.exec(select(Reminder).where(Reminder.trip_id == trip_id)).all()
    for reminder in reminders:
        session.delete(reminder)
        
    session.delete(trip)
    session.commit()
    return {"message": "Trip deleted"}

@router.patch("/{trip_id}", response_model=TripSchema)
def update_trip(trip_id: int, trip_in: TripUpdate, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    update_data = trip_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(trip, key, value)
    
    session.add(trip)
    session.commit()
    session.refresh(trip)
    return trip

@router.get("/{trip_id}/items", response_model=List[TripPackedItemSchema])
def read_trip_items(trip_id: int, session: Session = Depends(get_session)):
    statement = select(TripPackedItem).where(TripPackedItem.trip_id == trip_id)
    items = session.exec(statement).all()
    
    results = []
    for pi in items:
        # Get item detail separately
        item_obj = session.get(ItemModel, pi.item_id)
        
        # Build the response manually as a dict
        res_item = {
            "id": pi.id,
            "trip_id": pi.trip_id,
            "item_id": pi.item_id,
            "quantity": pi.quantity,
            "is_packed": pi.is_packed,
            "item_detail": item_obj.dict() if item_obj else None
        }
        results.append(res_item)
    return results

@router.patch("/items/{item_id}", response_model=TripPackedItemSchema)
def update_trip_item(item_id: int, is_packed: bool, session: Session = Depends(get_session)):
    item = session.get(TripPackedItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.is_packed = is_packed
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@router.get("/{trip_id}/weight")
def get_trip_weight_route(trip_id: int, session: Session = Depends(get_session)):
    weight = calculate_trip_weight(session, trip_id)
    return {"total_weight": weight}

@router.get("/{trip_id}/weather")
async def get_trip_weather_route(trip_id: int, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return await get_weather_forecast(trip.destination, trip.start_date, trip.end_date)

@router.get("/{trip_id}/pdf")
def export_trip_pdf_route(trip_id: int, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    items = session.exec(select(TripPackedItem).where(TripPackedItem.trip_id == trip_id)).all()
    for pi in items:
        pi.item = session.get(ItemModel, pi.item_id)
        if pi.item and pi.item.category_id:
            pi.item.category = session.get(Category, pi.item.category_id)
            
    pdf_content = generate_pdf(trip, items)
    return Response(
        content=bytes(pdf_content), 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=trip_{trip_id}.pdf"}
    )
