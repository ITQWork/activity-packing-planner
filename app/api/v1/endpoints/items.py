from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.models.models import Item
from app.schemas.schemas import Item as ItemSchema, ItemCreate

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
