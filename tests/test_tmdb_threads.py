import time
import concurrent.futures
import requests
import os
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def enrich_single_source(source):
    if not TMDB_API_KEY:
        return source
    title = source.get('title')
    start_t = time.time()
    try:
        tmdb_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
        tmdb_res = requests.get(tmdb_url, timeout=5).json()
        if tmdb_res.get('results') and len(tmdb_res['results']) > 0:
            top_hit = tmdb_res['results'][0]
            movie_id = top_hit.get('id')
            
            if movie_id:
                prov_url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={TMDB_API_KEY}"
                try:
                    requests.get(prov_url, timeout=5).json()
                except Exception:
                    pass
                
                cred_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_API_KEY}"
                try:
                    requests.get(cred_url, timeout=5).json()
                except Exception:
                    pass
    except Exception as e:
        print(f"Error on {title}: {e}")
    end_t = time.time()
    print(f"  - {title} finished in {end_t - start_t:.2f}s")
    return source

if __name__ == '__main__':
    sources = [
        {'title': 'Inception'},
        {'title': 'The Matrix'},
        {'title': 'Interstellar'},
        {'title': 'Blade Runner'},
        {'title': 'Arrival'}
    ]
    print("Testing Sequential Fetching...")
    seq_start = time.time()
    for s in sources:
        enrich_single_source(s)
    seq_end = time.time()
    print(f"Sequential Total: {seq_end - seq_start:.2f}s\n")
    
    print("Testing Parallel Fetching...")
    par_start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        list(executor.map(enrich_single_source, sources))
    par_end = time.time()
    print(f"Parallel Total: {par_end - par_start:.2f}s")
