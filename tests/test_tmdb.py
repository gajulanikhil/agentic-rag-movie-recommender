import os
from dotenv import load_dotenv
import requests

load_dotenv()
api_key = os.getenv("TMDB_API_KEY")

print(f"Loaded API Key: {api_key}")

if api_key:
    title = "Blade Runner 2049"
    tmdb_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={title}"
    try:
        res = requests.get(tmdb_url, timeout=5)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.json()}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("API Key is None!")
