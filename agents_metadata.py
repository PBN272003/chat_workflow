# agents_metadata.py
AGENT_LIST = [
    {
        "name": "ParserAgent",
        "description": "Extracts destination, travel dates, duration, and preferences from user input."
    },
    {
        "name": "WeatherAgent",
        "description": "Checks current and forecasted weather at the destination during travel dates. Advises if conditions are favorable for travel."
    },
    {
        "name": "FlightAgent",
        "description": "Searches for available flights from origin (assumed) to destination on departure and return dates. Returns top 3 options with price, airline, and duration."
    },
    {
        "name": "TourismAgent",
        "description": "Recommends top tourist attractions in the destination city. Includes name, rating, location, and brief history."
    },
    {
        "name": "TransportAgent",
        "description": "Provides information about public transport options (metro, bus, taxi) available in the destination city."
    },
    {
        "name": "HistoryAgent",
        "description": "Fetches historical and cultural background of key tourist locations from Wikipedia."
    }
]