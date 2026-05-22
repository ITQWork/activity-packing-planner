import httpx
from datetime import date, timedelta
from typing import Optional

async def get_weather_forecast(destination: str, start_date: date, end_date: Optional[date] = None):
    # This is a placeholder. In a real app, you'd use an API key.
    # API_KEY = os.getenv("OPENWEATHER_API_KEY")
    # For now, return mock data for each day of the trip.
    
    if not end_date:
        end_date = start_date
        
    forecasts = []
    current = start_date
    while current <= end_date:
        forecasts.append({
            "date": current.isoformat(),
            "forecast": "Sunny with a chance of clouds",
            "temp_high": 25 + (current.day % 5), # vary slightly
            "temp_low": 15 + (current.day % 3),
        })
        current += timedelta(days=1)
    
    return {
        "destination": destination,
        "forecasts": forecasts,
        "source": "Mock Multi-Day Weather Service"
    }
