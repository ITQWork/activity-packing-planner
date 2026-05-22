from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.models.models import Category, Item
from app.schemas.schemas import Category as CategorySchema, CategoryCreate, Message

router = APIRouter()

@router.post("/", response_model=CategorySchema)
def create_category(category_in: CategoryCreate, session: Session = Depends(get_session)):
    category = Category.from_orm(category_in)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

@router.get("/", response_model=List[CategorySchema])
def read_categories(session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()

@router.delete("/{category_id}", response_model=Message)
def delete_category(category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Update items that use this category to have no category
    items = session.exec(select(Item).where(Item.category_id == category_id)).all()
    for item in items:
        item.category_id = None
        session.add(item)
    
    session.delete(category)
    session.commit()
    return {"message": "Category deleted"}
