from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    class Config:
        from_attributes = True

class ItemBase(BaseModel):
    name: str
    unit_weight: float = 0.0
    category_id: Optional[int] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    class Config:
        from_attributes = True

class ActivityBase(BaseModel):
    name: str

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: int
    items_with_qty: Optional[List[dict]] = None
    class Config:
        from_attributes = True

class TripBase(BaseModel):
    destination: str
    start_date: date
    end_date: date
    activity_id: int
    user_id: Optional[int] = None

class TripCreate(TripBase):
    pass

class Trip(TripBase):
    id: int
    class Config:
        from_attributes = True

class TripPackedItemBase(BaseModel):
    trip_id: int
    item_id: int
    quantity: int
    is_packed: bool = False

class TripPackedItem(TripPackedItemBase):
    id: int
    item_detail: Optional[Item] = None
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class Message(BaseModel):
    message: str
