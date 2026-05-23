import os
import sys
import subprocess

def ensure_venv():
    """Ensures the script is running within the local virtual environment, creating it if necessary."""
    # Check if already in a venv
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        return

    # Check for venv directory
    venv_path = os.path.join(os.path.dirname(__file__), "venv")
    
    if not os.path.exists(venv_path):
        print(f"--- Creating virtual environment in {venv_path}... ---")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        
        # Determine pip path
        if os.name == 'nt':
            pip_exe = os.path.join(venv_path, "Scripts", "pip.exe")
        else:
            pip_exe = os.path.join(venv_path, "bin", "pip")
            
        print("--- Installing dependencies from plans/requirements.txt... ---")
        subprocess.run([pip_exe, "install", "-r", "plans/requirements.txt"], check=True)

    # Path to python executable in venv
    if os.name == 'nt':  # Windows
        python_exe = os.path.join(venv_path, "Scripts", "python.exe")
    else:  # Unix/macOS
        python_exe = os.path.join(venv_path, "bin", "python")

    if os.path.exists(python_exe):
        print(f"--- Relaunching using virtual environment at {venv_path} ---")
        # Re-execute the script using the venv's python
        os.execv(python_exe, [python_exe] + sys.argv)
    else:
        print("--- Warning: Virtual environment 'venv' found but python executable missing. ---")

# Run venv check before importing any dependencies
if __name__ == "__main__":
    ensure_venv()

import uvicorn
from sqlmodel import Session, SQLModel
from app.main import app
from app.db.session import engine
from app.models.models import User, Category, Item, Activity, ActivityItemLink, Trip
from app.services.packing import generate_trip_packing_list
from datetime import date, timedelta

def seed():
    # Initialize DB
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # 1. Create Admin User
        user = User(username="admin", password="password123")
        session.add(user)
        session.commit()
        session.refresh(user)

        # 2. Categories
        cats = ["Clothing", "Gear", "Toiletries", "Electronics", "Documents"]
        category_objs = {}
        for cat_name in cats:
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
            ("Drakensberg", "Alpine Hiking", today + timedelta(days=2), today + timedelta(days=5), False, None),
            ("Mauritius", "Beach Escape", today + timedelta(days=4), today + timedelta(days=11), False, None),
            ("St Andrews", "Golf Weekend", today + timedelta(days=15), today + timedelta(days=18), False, None),
            ("Tokyo", "City Tour", today + timedelta(days=45), today + timedelta(days=55), False, None),
            ("Swiss Alps", "Alpine Hiking", today - timedelta(days=60), today - timedelta(days=50), True, 5),
            ("Bali", "Beach Escape", today - timedelta(days=30), today - timedelta(days=20), True, 4),
            ("New York", "City Tour", today - timedelta(days=100), today - timedelta(days=90), True, 3),
        ]
        for dest, act_name, start, end, completed, rating in trips_data:
            trip = Trip(
                destination=dest,
                activity_id=activity_objs[act_name].id,
                user_id=user.id,
                start_date=start,
                end_date=end,
                is_completed=completed,
                rating=rating
            )
            session.add(trip)
            session.commit()
            session.refresh(trip)
            # Force generate packing list for seeded trips
            generate_trip_packing_list(session, trip)
        
        print("Rich test data seeded successfully!")

if __name__ == "__main__":
    if "--seed" in sys.argv:
        seed()
    
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
