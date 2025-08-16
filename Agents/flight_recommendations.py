#flight_recommendation_agent
import os
import re
import json
import requests
from amadeus import Client, ResponseError
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
from typing import List, Dict


load_dotenv()

amadeus = Client(
    client_id=os.getenv("AMADEUS_API_KEY"),
    client_secret=os.getenv("AMADEUS_API_SECRET")
)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

def format_duration(iso_duration: str) -> str:
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', iso_duration)
    hours = match.group(1) if match and match.group(1) else "0"
    minutes = match.group(2) if match and match.group(2) else "0"
    return f"{int(hours)}h {int(minutes)}m"

def get_airline_full_name(airline_code: str) -> str:
    prompt = f"Return only the full name of airline '{airline_code}' (e.g., 'Emirates'). No extra text."
    try:
        response = llm([HumanMessage(content=prompt)])
        return response.content.strip()
    except:
        return airline_code

def search_flights(origin: str, destination: str, departure_date: str, return_date: str = None, max_price: int = 2000) -> List[Dict]:
    try:
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": 1,
            "maxPrice": max_price
        }
        if return_date:
            params["returnDate"] = return_date

        response = amadeus.shopping.flight_offers_search.get(**params)
        flights = response.data

        results = []
        for flight in flights[:3]:
            price = float(flight['price']['total'])
            if price > max_price:
                continue

            # Outbound
            outbound = flight['itineraries'][0]
            segments = outbound['segments']
            carrier = segments[0]['carrierCode']
            airline = get_airline_full_name(carrier)
            dep = segments[0]['departure']['at']
            arr = segments[-1]['arrival']['at']
            dur = format_duration(outbound['duration'])

            # Return
            return_info = {}
            if return_date and len(flight['itineraries']) > 1:
                inbound = flight['itineraries'][1]
                r_segments = inbound['segments']
                r_dep = r_segments[0]['departure']['at']
                r_arr = r_segments[-1]['arrival']['at']
                r_dur = format_duration(inbound['duration'])
                return_info = {
                    "return_departure": r_dep,
                    "return_arrival": r_arr,
                    "return_duration": r_dur
                }

            results.append({
                "airline": airline,
                "price_usd": price,
                "departure": dep,
                "arrival": arr,
                "duration": dur,
                **return_info
            })
        return results
    except ResponseError as e:
        return [{"error": str(e)}]
    except Exception as e:
        return [{"error": "Unable to fetch flights"}]