from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.session import get_session
from app.models.models import User
from app.schemas.schemas import UserCreate, User as UserSchema, Message

router = APIRouter()

@router.post("/signup", response_model=UserSchema)
def signup(user_in: UserCreate, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.username == user_in.username)).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    user = User(username=user_in.username, password=user_in.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.post("/login")
def login(user_in: UserCreate, session: Session = Depends(get_session)):
    db_user = session.exec(
        select(User).where(User.username == user_in.username, User.password == user_in.password)
    ).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return {"message": "Login successful", "user_id": db_user.id, "username": db_user.username}
