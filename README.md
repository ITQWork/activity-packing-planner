# PackSmart | Activity Packing Planner

PackSmart is a web application designed to help you plan your trips by generating customized packing lists based on the activities you'll be doing.

## Features

- **User Authentication**: Secure your packing plans with a personal account.
- **Trip Planning**: Create trips by specifying a destination, start date, and activity.
- **Activity Templates**: Define reusable activity templates (e.g., Hiking, Golfing) with associated items.
- **Master Library**: Manage a global list of items with weights and categories.
- **Dynamic Checklists**: Automatically generate a packing checklist for every new trip.
- **Weight Tracking**: Monitor the total weight of your packed items.
- **Weather Integration**: Get a weather forecast for your destination to help you pack effectively.
- **PDF Export**: Export your final packing checklist as a PDF for easy access offline.

## Getting Started

### Prerequisites

- Python 3.7+
- All dependencies listed in `requirements.txt`

### Installation

1. Clone the repository to your local machine.
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize the database and seed it with initial data:
   ```bash
   python seed.py
   ```

### Running the App

Start the backend server using Uvicorn:
```bash
python -m uvicorn main:app --reload
```

The application will be available at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## How to Use

1. **Sign Up / Log In**: Create a new account or log into your existing one.
2. **Setup Activities (Optional)**: Visit the "Activities" tab to create templates for common activities. Add items from the library to these activities.
3. **Manage Library (Optional)**: Use the "Library" tab to add new items or categories to your master collection.
4. **Plan a Trip**: On the "Trips" tab, enter your destination, select an activity, and pick a start date.
5. **Pack**: Open your trip checklist, check off items as you pack them, and monitor your total gear weight.
6. **Export**: Click the PDF icon on any trip card to download a printable version of your checklist.

## Tech Stack

- **Backend**: FastAPI (Python), SQLModel (SQLAlchemy + Pydantic)
- **Database**: SQLite
- **Frontend**: Vue.js 3, Tailwind CSS, Axios
- **Services**: Custom Weather Service, PDF Generation Service

## Database Schema

The application uses SQLite with the following table definitions:

```sql
CREATE TABLE category (
	id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE activity (
	id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE item (
	id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	unit_weight FLOAT NOT NULL, 
	category_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES category (id)
);

CREATE TABLE trip (
	id INTEGER NOT NULL, 
	destination VARCHAR NOT NULL, 
	start_date DATE NOT NULL, 
	end_date DATE NOT NULL, 
	activity_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(activity_id) REFERENCES activity (id)
);

CREATE TABLE activityitemlink (
	activity_id INTEGER NOT NULL, 
	item_id INTEGER NOT NULL, 
	base_quantity INTEGER NOT NULL, 
	PRIMARY KEY (activity_id, item_id), 
	FOREIGN KEY(activity_id) REFERENCES activity (id), 
	FOREIGN KEY(item_id) REFERENCES item (id)
);

CREATE TABLE trippackeditem (
	id INTEGER NOT NULL, 
	trip_id INTEGER NOT NULL, 
	item_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	is_packed BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(trip_id) REFERENCES trip (id), 
	FOREIGN KEY(item_id) REFERENCES item (id)
);

CREATE TABLE reminder (
	id INTEGER NOT NULL, 
	text VARCHAR NOT NULL, 
	is_completed BOOLEAN NOT NULL, 
	trip_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(trip_id) REFERENCES trip (id)
);

CREATE TABLE user (
	id INTEGER NOT NULL, 
	username VARCHAR NOT NULL, 
	password VARCHAR NOT NULL, 
	PRIMARY KEY (id)
);
```
