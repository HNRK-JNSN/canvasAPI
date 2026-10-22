import os
import requests

# ==== CONFIGURATION ====
API_URL = "https://eaaa.instructure.com/api/v1"
ACCESS_TOKEN = os.environ["CANVAS_TOKEN"]  # Generate from Canvas user settings
USER_ID = 48025

url = f"{API_URL}/users/{USER_ID}"
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
resp = requests.get(url, headers=headers)
resp.raise_for_status()
print(resp.json()) #.get("avatar_url")