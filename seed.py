from sqlmodel import Session, create_engine, SQLModel, select
from models import Item, Category, Activity, ActivityItemLink, Trip, TripPackedItem
from logic import generate_trip_packing_list
from datetime import date

DATABASE_URL = "sqlite:///./packing_planner.db"
engine = create_engine(DATABASE_URL)

def seed_data():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Create Categories
        cat1 = Category(name="Clothing")
        cat2 = Category(name="Equipment")
        session.add(cat1)
        session.add(cat2)
        session.commit()
        session.refresh(cat1)
        session.refresh(cat2)

        # Create Items
        item1 = Item(name="Socks", unit_weight=50, category_id=cat1.id)
        item2 = Item(name="T-shirt", unit_weight=150, category_id=cat1.id)
        item3 = Item(name="Golf Club", unit_weight=500, category_id=cat2.id)
        session.add(item1)
        session.add(item2)
        session.add(item3)
        session.commit()
        session.refresh(item1)
        session.refresh(item2)
        session.refresh(item3)

        # Create Activity
        act = Activity(name="Golf Trip")
        session.add(act)
        session.commit()
        session.refresh(act)

        # Link items to Activity
        link1 = ActivityItemLink(activity_id=act.id, item_id=item1.id, base_quantity=1)
        link2 = ActivityItemLink(activity_id=act.id, item_id=item3.id, base_quantity=1)
        session.add(link1)
        session.add(link2)
        session.commit()

        # Create a Trip
        trip = Trip(destination="Pebble Beach", start_date=date(2026, 6, 1), end_date=date(2026, 6, 5), activity_id=act.id)
        session.add(trip)
        session.commit()
        session.refresh(trip)

        # Generate list
        generate_trip_packing_list(session, trip)
        
        print("Seed data created successfully!")

if __name__ == "__main__":
    seed_data()
