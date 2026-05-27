import os
import requests
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

FATSECRET_CLIENT_ID = os.getenv('FATSECRET_CLIENT_ID', 'DUMMY_CLIENT_ID')
FATSECRET_CLIENT_SECRET = os.getenv('FATSECRET_CLIENT_SECRET', 'DUMMY_CLIENT_SECRET')
TOKEN_URL = "https://oauth.fatsecret.com/connect/token"
API_URL = "https://platform.fatsecret.com/rest/server.api"

def get_access_token():
    """
    Authenticate with FatSecret using OAuth2 Client Credentials grant.
    Returns the Bearer token needed for API requests.
    """
    if FATSECRET_CLIENT_ID == 'DUMMY_CLIENT_ID':
        return "DUMMY_TOKEN"

    credentials = f"{FATSECRET_CLIENT_ID}:{FATSECRET_CLIENT_SECRET}"
    b64_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {b64_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "client_credentials",
        "scope": "basic"
    }
    
    try:
        response = requests.post(TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()
        return token_data.get("access_token")
    except Exception as e:
        print(f"Error fetching FatSecret token: {e}")
        return None

NUTRITION_CACHE = {}

def fetch_nutrition_for_food(food_name):
    """
    Search the FatSecret API for a given food name and extract its nutrition info.
    Uses an in-memory cache to prevent redundant API calls.
    """
    if food_name in NUTRITION_CACHE:
        return NUTRITION_CACHE[food_name]
        
    # Return dummy data if API keys are not configured yet
    if FATSECRET_CLIENT_ID == 'DUMMY_CLIENT_ID':
        dummy_data = {
            "food_name": food_name,
            "calories": 130.0,
            "protein": 2.0,
            "carbs": 28.0,
            "fat": 0.5
        }
        NUTRITION_CACHE[food_name] = dummy_data
        return dummy_data

    token = get_access_token()
    if not token:
        return None
        
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    def search_api(query):
        params = {
            "method": "foods.search",
            "search_expression": query,
            "format": "json",
            "region": "ID", # Prioritize Indonesian foods
            "max_results": 1
        }
        try:
            response = requests.get(API_URL, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("foods", {}).get("food", [])
        except Exception as e:
            print(f"Error fetching food data for {query}: {e}")
            return []

    # First attempt with exact food name
    foods = search_api(food_name)
    
    # Fallback attempt: If not found, try searching with just the first two words (e.g. "Ayam Goreng Tepung" -> "Ayam Goreng")
    if not foods and len(food_name.split()) > 1:
        fallback_query = " ".join(food_name.split()[:2])
        print(f"No results for '{food_name}'. Trying fallback search: '{fallback_query}'")
        foods = search_api(fallback_query)

    if not foods:
        print(f"Still no results for '{food_name}' or fallback. Returning dummy fallback.")
        # Fallback so the UI doesn't break and still shows the overlay
        fallback_data = {
            "food_name": food_name,
            "calories": 130.0,
            "protein": 2.0,
            "carbs": 28.0,
            "fat": 0.5
        }
        NUTRITION_CACHE[food_name] = fallback_data
        return fallback_data
        
    # If max_results=1, FatSecret sometimes returns a dict instead of a list
    first_food = foods[0] if isinstance(foods, list) else foods
    
    # The food_description usually contains string like: "Per 100g - Calories: 130kcal | Fat: 2.11g | Carbs: 28.59g | Protein: 2.69g"
    description = first_food.get("food_description", "")
    
    # Simple extraction logic (this requires regex or string splitting)
    # We will parse the standard FatSecret description format
    parsed_nutrition = parse_fatsecret_description(description)
    parsed_nutrition["food_name"] = first_food.get("food_name", food_name)
    
    NUTRITION_CACHE[food_name] = parsed_nutrition
    return parsed_nutrition

def parse_fatsecret_description(description):
    """
    Parse the standard FatSecret food description string to extract macros.
    Example input: "Per 100g - Calories: 130kcal | Fat: 2.11g | Carbs: 28.59g | Protein: 2.69g"
    """
    nutrition = {
        "calories": 0.0,
        "protein": 0.0,
        "carbs": 0.0,
        "fat": 0.0
    }
    
    try:
        parts = description.split('-')[-1].split('|')
        for part in parts:
            part = part.strip().lower()
            if "calories:" in part:
                val = part.replace("calories:", "").replace("kcal", "").strip()
                nutrition["calories"] = float(val)
            elif "fat:" in part:
                val = part.replace("fat:", "").replace("g", "").strip()
                nutrition["fat"] = float(val)
            elif "carbs:" in part:
                val = part.replace("carbs:", "").replace("g", "").strip()
                nutrition["carbs"] = float(val)
            elif "protein:" in part:
                val = part.replace("protein:", "").replace("g", "").strip()
                nutrition["protein"] = float(val)
    except Exception as e:
        print(f"Error parsing nutrition string: {e}")
        
    return nutrition
