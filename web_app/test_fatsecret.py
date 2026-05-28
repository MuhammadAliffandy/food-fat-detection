import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

FATSECRET_CLIENT_ID = os.getenv('FATSECRET_CLIENT_ID')
FATSECRET_CLIENT_SECRET = os.getenv('FATSECRET_CLIENT_SECRET')

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

r = requests.post("https://oauth.fatsecret.com/connect/token", headers=headers, data=data)
token = r.json().get("access_token")

params = {
    "method": "foods.search",
    "search_expression": "Perkedel Jagung",
    "format": "json",
    "region": "ID",
    "max_results": 1
}

res = requests.get("https://platform.fatsecret.com/rest/server.api", headers={"Authorization": f"Bearer {token}"}, params=params)
print(res.json())
