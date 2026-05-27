import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

FATSECRET_CLIENT_ID = os.getenv('FATSECRET_CLIENT_ID')
FATSECRET_CLIENT_SECRET = os.getenv('FATSECRET_CLIENT_SECRET')

if not FATSECRET_CLIENT_ID or FATSECRET_CLIENT_ID == 'DUMMY_CLIENT_ID':
    print("No real FatSecret keys found in .env!")
    exit(1)

# 1. Get OAuth Token
TOKEN_URL = "https://oauth.fatsecret.com/connect/token"
credentials = f"{FATSECRET_CLIENT_ID}:{FATSECRET_CLIENT_SECRET}"
b64_credentials = base64.b64encode(credentials.encode()).decode()

headers = {
    "Authorization": f"Basic {b64_credentials}",
    "Content-Type": "application/x-www-form-urlencoded"
}
data = {"grant_type": "client_credentials", "scope": "basic"}

print("Fetching token...")
response = requests.post(TOKEN_URL, headers=headers, data=data)
token_data = response.json()
token = token_data.get("access_token")

if not token:
    print("Failed to get token:", token_data)
    exit(1)

print("Token received! Fetching categories...")

# 2. Get Food Categories
API_URL = "https://platform.fatsecret.com/rest/food-categories/v2"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
params = {"format": "json", "region": "ID"}

res = requests.get(API_URL, headers=headers, params=params)
print("HTTP Status:", res.status_code)

try:
    import json
    print(json.dumps(res.json(), indent=2))
except Exception as e:
    print("Raw text:", res.text)
