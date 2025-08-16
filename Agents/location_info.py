from langchain_community.utilities import WikipediaAPIWrapper
from dotenv import load_dotenv
import os

load_dotenv()

api_wrapper = WikipediaAPIWrapper(top_k_results=3)

def get_location_history(query: str) -> str:
    try:
        full_summary = api_wrapper.run(query)
        return ". ".join(full_summary.split(". ")[:3]) + "."
    except:
        return "No historical information available."