# agents/public_transport_agent.py
import requests
from dotenv import load_dotenv
import os


load_dotenv()

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

def get_lat_lng(location: str) -> tuple:
    url = "https://api.geoapify.com/v1/geocode/search"
    params = {"text": location, "apiKey": GEOAPIFY_API_KEY}
    try:
        response = requests.get(url, params=params).json()
        if "features" in response and len(response["features"]) > 0:
            coords = response["features"][0]["geometry"]["coordinates"]
            return coords[1], coords[0]  # lat, lng
    except:
        pass
    return None, None

def get_public_transport(location: str, radius: int = 1000, limit: int = 5) -> list:
    lat, lng = get_lat_lng(location)
    if not lat or not lng:
        return [{"error": f"Could not locate {location}"}]

    url = "https://api.geoapify.com/v2/places"
    params = {
        "categories": "public_transport",
        "filter": f"circle:{lng},{lat},{radius}",
        "limit": limit,
        "apiKey": GEOAPIFY_API_KEY
    }

    try:
        response = requests.get(url, params=params).json()
        if "features" in response and len(response["features"]) > 0:
            transports = []
            for f in response["features"]:
                props = f["properties"]
                transports.append({
                    "name": props.get("name", "Unknown"),
                    "type": ", ".join(props.get("categories", [])),
                    "address": props.get("formatted", "Not available")
                })
            return transports
    except:
        pass
    return [{"error": "No transport hubs found or API error"}]