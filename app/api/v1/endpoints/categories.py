from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.models.models import Category
from app.schemas.schemas import Category as CategorySchema, CategoryCreate

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
