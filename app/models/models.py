from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import date

# Join Table for Activities and Items
class ActivityItemLink(SQLModel, table=True):
    activity_id: Optional[int] = Field(default=None, foreign_key="activity.id", primary_key=True)
    item_id: Optional[int] = Field(default=None, foreign_key="item.id", primary_key=True)
    base_quantity: int = 1

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    items: List["Item"] = Relationship(back_populates="category")

class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    unit_weight: float = 0.0  # in grams or kg, let's assume grams
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    category: Optional[Category] = Relationship(back_populates="items")
    activities: List["Activity"] = Relationship(back_populates="items", link_model=ActivityItemLink)

class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    items: List[Item] = Relationship(back_populates="activities", link_model=ActivityItemLink)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str  # In a real app, hash this!

class Trip(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    destination: str
    start_date: date
    end_date: date
    activity_id: int = Field(foreign_key="activity.id")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
    user: Optional[User] = Relationship()
    activity: Activity = Relationship()
    reminders: List["Reminder"] = Relationship(back_populates="trip")
    packed_items: List["TripPackedItem"] = Relationship(back_populates="trip")

class TripPackedItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int = Field(foreign_key="trip.id")
    item_id: int = Field(foreign_key="item.id")
    quantity: int
    is_packed: bool = False
    
    trip: Trip = Relationship(back_populates="packed_items")
    item: Item = Relationship()

class Reminder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    is_completed: bool = False
    trip_id: int = Field(foreign_key="trip.id")
    trip: Trip = Relationship(back_populates="reminders")
