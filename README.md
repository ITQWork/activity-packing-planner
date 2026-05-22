# PackSmart | Activity Packing Planner

PackSmart is a web application designed to help you plan your trips by generating customized packing lists based on the activities you'll be doing.

## Project Structure (Refactored)

The project follows a modular structure suitable for business environments:

```text
app/
├── api/                # API layer (v1 endpoints)
│   ├── deps.py         # Dependencies (get_db, etc.)
│   └── v1/
│       ├── api.py      # Main router inclusion
│       └── endpoints/  # Categorized routes (trips, activities, etc.)
├── core/               # App configuration (Pydantic Settings)
├── db/                 # Database connection and session management
├── models/             # SQLModel DB Models
├── schemas/            # Pydantic Schemas for validation and documentation
└── services/           # Business logic (PDF, Weather, Packing Logic)
main.py                 # Application entry point
```

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
python main.py
```

The application will be available at: [http://127.0.0.1:8000](http://127.0.0.1:8000)
API Documentation (Swagger UI): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Tech Stack

- **Backend**: FastAPI (Python), SQLModel (SQLAlchemy + Pydantic)
- **Database**: SQLite
- **Frontend**: Vue.js 3 (located in `static/`)
- **Services**: Custom Weather Service, PDF Generation Service (fpdf2)
- **Configuration**: Pydantic Settings
