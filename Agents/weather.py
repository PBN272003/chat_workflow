# agents/weather_agent.py
import requests
from dotenv import load_dotenv
import os


load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

def get_weather(city: str) -> dict:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url).json()
        if response.get("cod") != 200:
            return {"error": response.get("message", "City not found")}
        weather = response["weather"][0]["description"]
        temp = response["main"]["temp"]
        return {
            "city": city,
            "temperature_c": temp,
            "condition": weather
        }
    except Exception as e:
        return {"error": str(e)}