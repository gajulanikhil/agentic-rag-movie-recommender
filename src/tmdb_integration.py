"""
TMDB API Integration for Netflix GPT
Fetches movie posters, metadata, and additional information
"""

import requests
from typing import Optional, Dict, List
import os
from dotenv import load_dotenv
from functools import lru_cache
import time

# Load environment variables
load_dotenv()

class TMDBClient:
    """Client for TMDB API operations"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize TMDB client
        
        Args:
            api_key: TMDB API key (reads from .env if not provided)
        """
        self.api_key = api_key or os.getenv('TMDB_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "TMDB API key not found. Please set TMDB_API_KEY in .env file"
            )
        
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p"
        self.poster_sizes = ["w92", "w154", "w185", "w342", "w500", "w780", "original"]
        self.backdrop_sizes = ["w300", "w780", "w1280", "original"]
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.25  # 4 requests per second max
    
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """
        Make API request with error handling
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            Response JSON or None
        """
        self._rate_limit()
        
        if params is None:
            params = {}
        
        params['api_key'] = self.api_key
        
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                print(f"TMDB API error: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    @lru_cache(maxsize=500)
    def search_movie(self, title: str, year: Optional[int] = None) -> Optional[Dict]:
        """
        Search for a movie by title
        
        Args:
            title: Movie title
            year: Release year (optional, improves accuracy)
            
        Returns:
            Movie data or None
        """
        params = {
            'query': title,
            'include_adult': False,
            'language': 'en-US',
            'page': 1
        }
        
        if year:
            params['year'] = year
        
        data = self._make_request('search/movie', params)
        
        if data and data.get('results'):
            # Return first result (most relevant)
            return data['results'][0]
        
        return None
    
    def get_poster_url(
        self, 
        poster_path: Optional[str], 
        size: str = "w500"
    ) -> Optional[str]:
        """
        Get full poster URL
        
        Args:
            poster_path: Poster path from TMDB
            size: Image size (w92, w154, w185, w342, w500, w780, original)
            
        Returns:
            Full poster URL or None
        """
        if not poster_path:
            return None
        
        if size not in self.poster_sizes:
            size = "w500"
        
        return f"{self.image_base_url}/{size}{poster_path}"
    
    def get_backdrop_url(
        self, 
        backdrop_path: Optional[str], 
        size: str = "w780"
    ) -> Optional[str]:
        """
        Get full backdrop URL
        
        Args:
            backdrop_path: Backdrop path from TMDB
            size: Image size (w300, w780, w1280, original)
            
        Returns:
            Full backdrop URL or None
        """
        if not backdrop_path:
            return None
        
        if size not in self.backdrop_sizes:
            size = "w780"
        
        return f"{self.image_base_url}/{size}{backdrop_path}"
    
    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """
        Get detailed movie information
        
        Args:
            movie_id: TMDB movie ID
            
        Returns:
            Movie details or None
        """
        return self._make_request(f'movie/{movie_id}')
    
    def get_movie_images(
        self, 
        title: str, 
        year: Optional[int] = None
    ) -> Dict[str, Optional[str]]:
        """
        Get movie poster and backdrop URLs
        
        Args:
            title: Movie title
            year: Release year
            
        Returns:
            Dictionary with poster and backdrop URLs
        """
        movie = self.search_movie(title, year)
        
        if not movie:
            return {
                'poster_url': None,
                'backdrop_url': None,
                'tmdb_id': None,
                'title': title,
                'year': year
            }
        
        return {
            'poster_url': self.get_poster_url(movie.get('poster_path')),
            'backdrop_url': self.get_backdrop_url(movie.get('backdrop_path')),
            'tmdb_id': movie.get('id'),
            'title': movie.get('title', title),
            'year': year,
            'overview': movie.get('overview'),
            'vote_average': movie.get('vote_average'),
            'popularity': movie.get('popularity')
        }
    
    def get_multiple_movie_images(
        self, 
        movies: List[Dict[str, any]]
    ) -> List[Dict]:
        """
        Get images for multiple movies
        
        Args:
            movies: List of movie dicts with 'title' and optional 'year'
            
        Returns:
            List of movie data with image URLs
        """
        results = []
        
        for movie in movies:
            title = movie.get('title')
            year = movie.get('year')
            
            if not title:
                continue
            
            images = self.get_movie_images(title, year)
            
            # Merge with original movie data
            movie_data = {**movie, **images}
            results.append(movie_data)
        
        return results


class TMDBCache:
    """Simple cache for TMDB results"""
    
    def __init__(self, cache_file: str = "data/tmdb_cache.json"):
        """Initialize cache"""
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cache from file"""
        import json
        from pathlib import Path
        
        cache_path = Path(self.cache_file)
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        
        return {}
    
    def _save_cache(self):
        """Save cache to file"""
        import json
        from pathlib import Path
        
        cache_path = Path(self.cache_file)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(cache_path, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def get(self, title: str, year: Optional[int] = None) -> Optional[Dict]:
        """Get from cache"""
        key = f"{title}_{year}" if year else title
        return self.cache.get(key)
    
    def set(self, title: str, data: Dict, year: Optional[int] = None):
        """Save to cache"""
        key = f"{title}_{year}" if year else title
        self.cache[key] = data
        self._save_cache()


# Convenience functions
def get_movie_poster(
    title: str, 
    year: Optional[int] = None,
    size: str = "w500",
    use_cache: bool = True
) -> Optional[str]:
    """
    Quick function to get movie poster URL
    
    Args:
        title: Movie title
        year: Release year
        size: Poster size
        use_cache: Use cached results
        
    Returns:
        Poster URL or None
    """
    if use_cache:
        cache = TMDBCache()
        cached = cache.get(title, year)
        
        if cached:
            return cached.get('poster_url')
    
    try:
        client = TMDBClient()
        images = client.get_movie_images(title, year)
        poster_url = images.get('poster_url')
        
        if use_cache and poster_url:
            cache.set(title, images, year)
        
        return poster_url
        
    except Exception as e:
        print(f"Error getting poster: {e}")
        return None


def get_multiple_posters(movies: List[Dict]) -> List[Dict]:
    """
    Get posters for multiple movies with caching
    
    Args:
        movies: List of movie dicts
        
    Returns:
        List with poster URLs added
    """
    try:
        client = TMDBClient()
        cache = TMDBCache()
        results = []
        
        for movie in movies:
            title = movie.get('title')
            year = movie.get('year')
            
            # Check cache first
            cached = cache.get(title, year)
            if cached:
                results.append({**movie, **cached})
                continue
            
            # Fetch from API
            images = client.get_movie_images(title, year)
            cache.set(title, images, year)
            
            results.append({**movie, **images})
        
        return results
        
    except Exception as e:
        print(f"Error getting multiple posters: {e}")
        return movies


# Test function
def test_tmdb_integration():
    """Test TMDB integration"""
    
    print("\n" + "="*70)
    print("TESTING TMDB INTEGRATION")
    print("="*70 + "\n")
    
    try:
        # Initialize client
        print("1️⃣ Initializing TMDB client...")
        client = TMDBClient()
        print("   ✅ Client initialized\n")
        
        # Test single movie search
        print("2️⃣ Testing single movie search...")
        images = client.get_movie_images("The Dark Knight", 2008)
        
        print(f"   Title: {images.get('title')}")
        print(f"   TMDB ID: {images.get('tmdb_id')}")
        print(f"   Poster URL: {images.get('poster_url')[:50]}..." if images.get('poster_url') else "   No poster found")
        print(f"   Rating: {images.get('vote_average')}/10\n")
        
        # Test multiple movies
        print("3️⃣ Testing multiple movies...")
        test_movies = [
            {'title': 'Inception', 'year': 2010},
            {'title': 'The Matrix', 'year': 1999},
            {'title': 'Interstellar', 'year': 2014}
        ]
        
        results = client.get_multiple_movie_images(test_movies)
        
        for result in results:
            has_poster = "✅" if result.get('poster_url') else "❌"
            print(f"   {has_poster} {result.get('title')} ({result.get('year')})")
        print()
        
        # Test caching
        print("4️⃣ Testing cache...")
        cache = TMDBCache()
        
        # Save to cache
        cache.set("Test Movie", images, 2024)
        
        # Retrieve from cache
        cached = cache.get("Test Movie", 2024)
        
        if cached:
            print("   ✅ Cache working\n")
        else:
            print("   ❌ Cache not working\n")
        
        # Test convenience function
        print("5️⃣ Testing convenience function...")
        poster_url = get_movie_poster("The Shawshank Redemption", 1994)
        
        if poster_url:
            print(f"   ✅ Poster URL: {poster_url[:50]}...\n")
        else:
            print("   ❌ No poster found\n")
        
        print("="*70)
        print("✅ TMDB INTEGRATION TEST COMPLETE")
        print("="*70 + "\n")
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease ensure:")
        print("1. You have created a .env file in the project root")
        print("2. Added your TMDB API key: TMDB_API_KEY=your_key_here\n")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_tmdb_integration()