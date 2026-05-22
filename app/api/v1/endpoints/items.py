from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.models.models import Item, ActivityItemLink, TripPackedItem
from app.schemas.schemas import Item as ItemSchema, ItemCreate, Message

router = APIRouter()

@router.post("/", response_model=ItemSchema)
def create_item(item_in: ItemCreate, session: Session = Depends(get_session)):
    item = Item.from_orm(item_in)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@router.get("/", response_model=List[ItemSchema])
def read_items(session: Session = Depends(get_session)):
    return session.exec(select(Item)).all()

@router.delete("/{item_id}", response_model=Message)
def delete_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Delete links to activities
    links = session.exec(select(ActivityItemLink).where(ActivityItemLink.item_id == item_id)).all()
    for link in links:
        session.delete(link)
    
    # Delete from trip packing lists
    packed_items = session.exec(select(TripPackedItem).where(TripPackedItem.item_id == item_id)).all()
    for pi in packed_items:
        session.delete(pi)
    
    session.delete(item)
    session.commit()
    return {"message": "Item deleted from library"}
