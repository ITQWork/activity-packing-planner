from sqlmodel import Session, create_engine, select
from models import User, Category, Item, Activity, ActivityItemLink, Trip
from datetime import date, timedelta

DATABASE_URL = "sqlite:///./packing_planner.db"
engine = create_engine(DATABASE_URL)

def seed():
    with Session(engine) as session:
        # 1. Get or Create User
        user = session.exec(select(User).where(User.id == 1)).first()
        if not user:
            user = User(id=1, username="admin", password="password123")
            session.add(user)
            session.commit()
            session.refresh(user)

        # 2. Categories
        cats = ["Clothing", "Gear", "Toiletries", "Electronics", "Documents"]
        category_objs = {}
        for cat_name in cats:
            cat = session.exec(select(Category).where(Category.name == cat_name)).first()
            if not cat:
                cat = Category(name=cat_name)
                session.add(cat)
                session.commit()
                session.refresh(cat)
            category_objs[cat_name] = cat

        # 3. Items
        items_data = [
            ("Hiking Boots", "Gear", 1200),
            ("Rain Jacket", "Clothing", 400),
            ("Water Bottle", "Gear", 200),
            ("Sunscreen", "Toiletries", 100),
            ("Passport", "Documents", 50),
            ("Power Bank", "Electronics", 300),
            ("Wool Socks", "Clothing", 100),
            ("Golf Clubs", "Gear", 5000),
            ("Golf Polo", "Clothing", 250),
            ("Swim Trunks", "Clothing", 200),
            ("Beach Towel", "Gear", 600),
            ("Camera", "Electronics", 800),
        ]
        item_objs = {}
        for name, cat_name, weight in items_data:
            item = session.exec(select(Item).where(Item.name == name)).first()
            if not item:
                item = Item(name=name, unit_weight=weight, category_id=category_objs[cat_name].id)
                session.add(item)
                session.commit()
                session.refresh(item)
            item_objs[name] = item

        # 4. Activities
        activities_data = {
            "Alpine Hiking": ["Hiking Boots", "Rain Jacket", "Water Bottle", "Wool Socks", "Power Bank"],
            "Golf Weekend": ["Golf Clubs", "Golf Polo", "Sunscreen", "Power Bank"],
            "Beach Escape": ["Swim Trunks", "Beach Towel", "Sunscreen", "Camera"],
            "City Tour": ["Passport", "Camera", "Power Bank", "Rain Jacket"]
        }
        activity_objs = {}
        for act_name, item_names in activities_data.items():
            act = session.exec(select(Activity).where(Activity.name == act_name)).first()
            if not act:
                act = Activity(name=act_name)
                session.add(act)
                session.commit()
                session.refresh(act)
                # Link items
                for i_name in item_names:
                    link = ActivityItemLink(activity_id=act.id, item_id=item_objs[i_name].id, base_quantity=1)
                    session.add(link)
                session.commit()
            activity_objs[act_name] = act

        # 5. Trips
        today = date.today()
        trips_data = [
            ("Drakensberg", "Alpine Hiking", today + timedelta(days=2), today + timedelta(days=5)),
            ("Mauritius", "Beach Escape", today + timedelta(days=4), today + timedelta(days=11)),
            ("St Andrews", "Golf Weekend", today + timedelta(days=15), today + timedelta(days=18)),
            ("Tokyo", "City Tour", today + timedelta(days=45), today + timedelta(days=55)),
        ]
        for dest, act_name, start, end in trips_data:
            existing = session.exec(select(Trip).where(Trip.destination == dest, Trip.user_id == user.id)).first()
            if not existing:
                trip = Trip(
                    destination=dest,
                    activity_id=activity_objs[act_name].id,
                    user_id=user.id,
                    start_date=start,
                    end_date=end
                )
                session.add(trip)
                session.commit()
                # Force generate packing list for seeded trips
                from logic import generate_trip_packing_list
                generate_trip_packing_list(session, trip)
        
        print("Test data seeded successfully!")

if __name__ == "__main__":
    seed()
