import os
import requests
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
import warnings
warnings.filterwarnings("ignore")
import google.generativeai as genai
from langchain_community.tools import DuckDuckGoSearchRun,WikipediaQueryRun
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()


#GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
MAPS_API_KEY = os.getenv("google_maps_api_key")
# agents/tourism_agent.py
def get_lat_lng(location_name: str) -> str:
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location_name}&key={MAPS_API_KEY}"
    try:
        response = requests.get(geocode_url)
        if response.status_code == 200:
            geo_data = response.json()
            if geo_data['results']:
                loc = geo_data['results'][0]['geometry']['location']
                return f"{loc['lat']},{loc['lng']}"
    except:
        pass
    return "Location not found."

def get_tourist_places(location_name: str) -> List[Dict]:
    lat_lng = get_lat_lng(location_name)
    if "not found" in lat_lng:
        return [{"error": lat_lng}]

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": lat_lng,
        "radius": 30000,
        "type": "tourist_attraction",
        "key": MAPS_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            places = response.json().get('results', [])
            return [
                {"name": p['name'], "rating": p.get("rating", "N/A"), "vicinity": p['vicinity']}
                for p in places[:5]
            ]
    except:
        pass
    return [{"error": "Failed to fetch tourist places"}]

def get_place_history(place_name: str) -> str:
    wikipedia_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{place_name.replace(' ', '_')}"
    try:
        response = requests.get(wikipedia_url)
        if response.status_code == 200:
            data = response.json()
            return data.get("extract", "No history available.")
    except:
        pass
    return "No history available."

def suggest_attractions(destination: str) -> List[Dict]:
    places = get_tourist_places(destination)
    if "error" in places[0]:
        return places

    enriched = []
    for place in places:
        history = get_place_history(place["name"])
        enriched.append({
            "name": place["name"],
            "rating": place["rating"],
            "location": place["vicinity"],
            "history": history
        })
    return enriched