from sqlmodel import SQLModel, create_engine, Session, select
from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import List
from models import Item, Category, Activity, ActivityItemLink, Trip, TripPackedItem, Reminder, User
from logic import generate_trip_packing_list, calculate_trip_weight
from weather_service import get_weather_forecast

print("--- main.py LOADED ---")

# Database Setup
DATABASE_URL = "sqlite:///./packing_planner.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# FastAPI App
app = FastAPI(title="Activity Packing Planner")

print("--- FastAPI APP INITIALIZED ---")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    print("--- SERVER STARTUP EVENT ---")
    create_db_and_tables()

# --- Authentication ---
@app.post("/signup")
def signup(user: User, session: Session = Depends(get_session)):
    print(f"--- SIGNUP CALLED for {user.username} ---")
    db_user = session.exec(select(User).where(User.username == user.username)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User created", "user_id": user.id, "username": user.username}

@app.post("/login")
def login(user: User, session: Session = Depends(get_session)):
    print(f"--- LOGIN CALLED for {user.username} ---")
    db_user = session.exec(select(User).where(User.username == user.username, User.password == user.password)).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": db_user.id, "username": db_user.username}

# --- Categories ---
@app.post("/categories")
def create_category(category: Category, session: Session = Depends(get_session)):
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

@app.get("/categories")
def read_categories(session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()

# --- Items ---
@app.post("/items")
def create_item(item: Item, session: Session = Depends(get_session)):
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@app.get("/items")
def read_items(session: Session = Depends(get_session)):
    return session.exec(select(Item)).all()

# --- Activities ---
@app.post("/activities")
def create_activity(activity: Activity, session: Session = Depends(get_session)):
    session.add(activity)
    session.commit()
    session.refresh(activity)
    return activity

@app.get("/activities")
def read_activities(session: Session = Depends(get_session)):
    activities = session.exec(select(Activity)).all()
    results = []
    for activity in activities:
        activity_data = activity.dict()
        links = session.exec(select(ActivityItemLink).where(ActivityItemLink.activity_id == activity.id)).all()
        items_with_qty = []
        for link in links:
            item = session.get(Item, link.item_id)
            if item:
                item_dict = item.dict()
                item_dict['base_quantity'] = link.base_quantity
                items_with_qty.append(item_dict)
        activity_data['items_with_qty'] = items_with_qty
        results.append(activity_data)
    return results

@app.delete("/activities/{activity_id}")
def delete_activity(activity_id: int, session: Session = Depends(get_session)):
    activity = session.get(Activity, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Check if any trips are using this activity
    trips = session.exec(select(Trip).where(Trip.activity_id == activity_id)).all()
    if trips:
        raise HTTPException(status_code=400, detail="Cannot delete activity used by existing trips")
        
    # Delete links first
    links = session.exec(select(ActivityItemLink).where(ActivityItemLink.activity_id == activity_id)).all()
    for link in links:
        session.delete(link)
        
    session.delete(activity)
    session.commit()
    return {"message": "Activity deleted"}

@app.post("/activities/{activity_id}/items/{item_id}")
def add_item_to_activity(activity_id: int, item_id: int, base_quantity: int = 1, session: Session = Depends(get_session)):
    # Check if link already exists
    link = session.get(ActivityItemLink, (activity_id, item_id))
    if link:
        link.base_quantity = base_quantity
    else:
        link = ActivityItemLink(activity_id=activity_id, item_id=item_id, base_quantity=base_quantity)
    session.add(link)
    session.commit()
    return {"message": "Item added/updated in activity"}

# --- Trips ---
@app.post("/trips")
def create_trip(trip_data: dict, session: Session = Depends(get_session)):
    from datetime import datetime
    
    # Manually parse dates because of SQLite/SQLModel string vs date object issues
    start_date = datetime.strptime(trip_data["start_date"], "%Y-%m-%d").date()
    end_date = datetime.strptime(trip_data["end_date"], "%Y-%m-%d").date()
    
    trip = Trip(
        destination=trip_data["destination"],
        start_date=start_date,
        end_date=end_date,
        activity_id=trip_data["activity_id"],
        user_id=trip_data["user_id"]
    )
    
    session.add(trip)
    session.commit()
    session.refresh(trip)
    
    # Force link generation using logic.py
    from logic import generate_trip_packing_list
    generate_trip_packing_list(session, trip)
    
    return trip

@app.get("/trips")
def read_trips(user_id: int = None, session: Session = Depends(get_session)):
    query = select(Trip)
    if user_id:
        query = query.where(Trip.user_id == user_id)
    return session.exec(query).all()

@app.delete("/trips/{trip_id}")
def delete_trip(trip_id: int, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Delete packed items first
    packed_items = session.exec(select(TripPackedItem).where(TripPackedItem.trip_id == trip_id)).all()
    for item in packed_items:
        session.delete(item)
    
    # Delete reminders
    reminders = session.exec(select(Reminder).where(Reminder.trip_id == trip_id)).all()
    for reminder in reminders:
        session.delete(reminder)
        
    session.delete(trip)
    session.commit()
    return {"message": "Trip deleted"}

@app.get("/trips/{trip_id}/items")
def read_trip_items(trip_id: int, session: Session = Depends(get_session)):
    items = session.exec(select(TripPackedItem).where(TripPackedItem.trip_id == trip_id)).all()
    # Eagerly load item details for weight/name
    results = []
    for item in items:
        item_dict = item.dict()
        item_detail = session.get(Item, item.item_id)
        if item_detail:
            item_dict['item_detail'] = item_detail.dict()
        results.append(item_dict)
    return results

@app.patch("/trip-items/{item_id}")
def update_trip_item(item_id: int, is_packed: bool, session: Session = Depends(get_session)):
    item = session.get(TripPackedItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.is_packed = is_packed
    session.add(item)
    session.commit()
    return item

@app.get("/trips/{trip_id}/weight")
def get_trip_weight(trip_id: int, session: Session = Depends(get_session)):
    weight = calculate_trip_weight(session, trip_id)
    return {"total_weight": weight}

@app.get("/trips/{trip_id}/weather")
async def get_trip_weather(trip_id: int, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return await get_weather_forecast(trip.destination, trip.start_date, trip.end_date)

# --- PDF Export ---
@app.get("/trips/{trip_id}/pdf")
def export_trip_pdf(trip_id: int, session: Session = Depends(get_session)):
    from pdf_service import generate_pdf
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    items = session.exec(select(TripPackedItem).where(TripPackedItem.trip_id == trip_id)).all()
    for pi in items:
        pi.item_detail = session.get(Item, pi.item_id)
        if pi.item_detail.category_id:
            pi.category = session.get(Category, pi.item_detail.category_id)
            
    pdf_content = generate_pdf(trip, items)
    return Response(content=pdf_content, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=trip_{trip_id}.pdf"})

# --- Debug ---
@app.get("/debug-routes")
def debug_routes():
    return [{"path": route.path, "name": route.name, "methods": route.methods} for route in app.routes]

# --- Frontend ---
@app.get("/")
def get_index():
    print("--- GET INDEX CALLED ---")
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())
