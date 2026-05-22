from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.models.models import Activity, ActivityItemLink, Item, Trip
from app.schemas.schemas import Activity as ActivitySchema, ActivityCreate, Message

router = APIRouter()

@router.post("/", response_model=ActivitySchema)
def create_activity(activity_in: ActivityCreate, session: Session = Depends(get_session)):
    activity = Activity.from_orm(activity_in)
    session.add(activity)
    session.commit()
    session.refresh(activity)
    return activity

@router.get("/", response_model=List[ActivitySchema])
def read_activities(session: Session = Depends(get_session)):
    activities = session.exec(select(Activity)).all()
    results = []
    for activity in activities:
        activity_data = activity.dict()
        links = session.exec(
            select(ActivityItemLink).where(ActivityItemLink.activity_id == activity.id)
        ).all()
        items_with_qty = []
        for link in links:
            item = session.get(Item, link.item_id)
            if item:
                item_dict = item.dict()
                item_dict['base_quantity'] = link.base_quantity
                items_with_qty.append(item_dict)
        activity_data['items_with_qty'] = items_with_qty
        results.append(activity_data)
    return results

@router.delete("/{activity_id}", response_model=Message)
def delete_activity(activity_id: int, session: Session = Depends(get_session)):
    activity = session.get(Activity, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Check if any trips are using this activity
    trips = session.exec(select(Trip).where(Trip.activity_id == activity_id)).all()
    if trips:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cannot delete activity used by existing trips"
        )
        
    # Delete links first
    links = session.exec(
        select(ActivityItemLink).where(ActivityItemLink.activity_id == activity_id)
    ).all()
    for link in links:
        session.delete(link)
        
    session.delete(activity)
    session.commit()
    return {"message": "Activity deleted"}

@router.post("/{activity_id}/items/{item_id}", response_model=Message)
def add_item_to_activity(
    activity_id: int, 
    item_id: int, 
    base_quantity: int = 1, 
    session: Session = Depends(get_session)
):
    # Check if link already exists
    link = session.get(ActivityItemLink, (activity_id, item_id))
    if link:
        link.base_quantity = base_quantity
    else:
        link = ActivityItemLink(activity_id=activity_id, item_id=item_id, base_quantity=base_quantity)
    session.add(link)
    session.commit()
    return {"message": "Item added/updated in activity"}
