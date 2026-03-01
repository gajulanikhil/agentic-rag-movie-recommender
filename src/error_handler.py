"""
Error handling and validation for Netflix GPT
"""

import time
import requests
from typing import Optional, Callable, Any, Dict
from functools import wraps
import traceback


class NetflixGPTError(Exception):
    """Base exception for Netflix GPT errors"""
    pass


class OllamaConnectionError(NetflixGPTError):
    """Raised when Ollama is not available"""
    pass


class VectorStoreError(NetflixGPTError):
    """Raised when vector store has issues"""
    pass


class QueryValidationError(NetflixGPTError):
    """Raised when query validation fails"""
    pass


class NoResultsError(NetflixGPTError):
    """Raised when no results are found"""
    pass


class ErrorHandler:
    """Centralized error handling and validation"""
    
    @staticmethod
    def validate_query(query: str) -> tuple[bool, Optional[str]]:
        """
        Validate user query
        
        Args:
            query: User's input query
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if empty
        if not query or not query.strip():
            return False, "Query cannot be empty. Please ask a question about movies."
        
        # Check length
        if len(query.strip()) < 3:
            return False, "Query is too short. Please provide more detail (at least 3 characters)."
        
        if len(query) > 500:
            return False, "Query is too long (max 500 characters). Please be more concise."
        
        # Check for special characters only
        if not any(c.isalnum() for c in query):
            return False, "Query must contain letters or numbers."
        
        return True, None
    
    @staticmethod
    def check_ollama_connection(base_url: str = "http://localhost:11434") -> tuple[bool, Optional[str]]:
        """
        Check if Ollama is running and accessible
        
        Args:
            base_url: Ollama base URL
            
        Returns:
            Tuple of (is_connected, error_message)
        """
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return True, None
            else:
                return False, f"Ollama returned status code {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, (
                "Cannot connect to Ollama. Please make sure:\n"
                "  1. Ollama is installed (https://ollama.ai)\n"
                "  2. Ollama is running: 'ollama serve'\n"
                "  3. A model is downloaded: 'ollama pull llama3.2'"
            )
        except requests.exceptions.Timeout:
            return False, "Connection to Ollama timed out. Check if Ollama is running."
        except Exception as e:
            return False, f"Unexpected error checking Ollama: {str(e)}"
    
    @staticmethod
    def validate_vector_store(vector_store) -> tuple[bool, Optional[str]]:
        """
        Validate vector store is properly initialized
        
        Args:
            vector_store: VectorStore instance
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not hasattr(vector_store, 'collection') or vector_store.collection is None:
                return False, "Vector store not properly initialized. Please run setup."
            
            count = vector_store.collection.count()
            if count == 0:
                return False, (
                    "Vector store is empty. Please run:\n"
                    "  python src/vectorstore.py"
                )
            
            if count < 10:
                return False, (
                    f"Vector store has only {count} chunks (minimum 10 required).\n"
                    "Please re-run data ingestion:\n"
                    "  python src/data_ingestion.py\n"
                    "  python src/vectorstore.py"
                )
            
            return True, None
            
        except Exception as e:
            return False, f"Error validating vector store: {str(e)}"
    
    @staticmethod
    def handle_empty_results(query: str) -> Dict[str, Any]:
        """
        Generate helpful response when no results found
        
        Args:
            query: Original query
            
        Returns:
            Response dictionary with suggestions
        """
        suggestions = [
            "Try broader terms (e.g., 'action movies' instead of specific titles)",
            "Check spelling of movie names or genres",
            "Try different keywords or phrases",
            "Ask about movie genres, moods, or themes instead"
        ]
        
        return {
            'answer': (
                "I couldn't find relevant movies for your query. Here are some suggestions:\n\n"
                + "\n".join(f"• {s}" for s in suggestions) + "\n\n"
                "You can also try queries like:\n"
                "• 'Recommend action movies'\n"
                "• 'Show me comedies from the 90s'\n"
                "• 'Movies for a relaxing evening'"
            ),
            'suggestions': suggestions,
            'original_query': query
        }


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry function on failure
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        print(f"⚠️  Attempt {attempt + 1} failed: {str(e)}")
                        print(f"   Retrying in {current_delay:.1f}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        print(f"❌ All {max_retries + 1} attempts failed")
            
            raise last_exception
        
        return wrapper
    return decorator


def safe_execute(func: Callable, fallback_value: Any = None, error_message: str = None):
    """
    Safely execute a function with error handling
    
    Args:
        func: Function to execute
        fallback_value: Value to return on error
        error_message: Custom error message
        
    Returns:
        Function result or fallback value
    """
    try:
        return func()
    except Exception as e:
        if error_message:
            print(f"⚠️  {error_message}: {str(e)}")
        else:
            print(f"⚠️  Error in {func.__name__}: {str(e)}")
        return fallback_value


class InputValidator:
    """Validate and sanitize user inputs"""
    
    @staticmethod
    def sanitize_query(query: str) -> str:
        """
        Sanitize user query
        
        Args:
            query: Raw user input
            
        Returns:
            Sanitized query
        """
        if not query:
            return ""
        
        # Remove leading/trailing whitespace
        query = query.strip()
        
        # Replace multiple spaces with single space
        query = ' '.join(query.split())
        
        # Remove control characters
        query = ''.join(char for char in query if ord(char) >= 32 or char == '\n')
        
        return query
    
    @staticmethod
    def validate_filters(filters: Optional[Dict]) -> tuple[bool, Optional[str]]:
        """
        Validate metadata filters
        
        Args:
            filters: Filter dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if filters is None:
            return True, None
        
        if not isinstance(filters, dict):
            return False, "Filters must be a dictionary"
        
        # Validate filter keys
        valid_keys = ['genre', 'year', 'director', 'type']
        for key in filters.keys():
            if key not in valid_keys:
                return False, f"Invalid filter key: {key}. Valid keys: {valid_keys}"
        
        # Validate year if present
        if 'year' in filters:
            year = filters['year']
            if not isinstance(year, int) or year < 1900 or year > 2030:
                return False, f"Invalid year: {year}. Must be between 1900-2030"
        
        return True, None
    
    @staticmethod
    def validate_file_path(filepath: str) -> tuple[bool, Optional[str]]:
        """
        Validate file path for save/load operations
        
        Args:
            filepath: Path to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filepath:
            return False, "File path cannot be empty"
        
        # Check for dangerous characters
        dangerous_chars = ['..', '~', '$', '`']
        if any(char in filepath for char in dangerous_chars):
            return False, "File path contains invalid characters"
        
        # Check extension for JSON files
        if not filepath.endswith('.json'):
            return False, "File must have .json extension"
        
        return True, None


# Test function
def test_error_handling():
    """Test error handling functionality"""
    
    print("\n" + "="*70)
    print("TESTING ERROR HANDLING")
    print("="*70 + "\n")
    
    handler = ErrorHandler()
    validator = InputValidator()
    
    # Test 1: Query validation
    print("1️⃣ Testing query validation:\n")
    
    test_queries = [
        ("", "Empty query"),
        ("hi", "Too short"),
        ("a" * 600, "Too long"),
        ("!!!!", "Special chars only"),
        ("Recommend action movies", "Valid query")
    ]
    
    for query, description in test_queries:
        is_valid, error = handler.validate_query(query)
        status = "✅" if is_valid else "❌"
        print(f"{status} {description}: {'Valid' if is_valid else error}")
    
    # Test 2: Ollama connection
    print("\n2️⃣ Testing Ollama connection:\n")
    is_connected, error = handler.check_ollama_connection()
    if is_connected:
        print("✅ Ollama is running and accessible")
    else:
        print(f"❌ Ollama issue:\n{error}")
    
    # Test 3: Input sanitization
    print("\n3️⃣ Testing input sanitization:\n")
    
    test_inputs = [
        "  extra   spaces  ",
        "multiple\n\nlines\nhere",
        "Special chars: @#$%",
    ]
    
    for input_text in test_inputs:
        sanitized = validator.sanitize_query(input_text)
        print(f"Original: {repr(input_text)}")
        print(f"Sanitized: {repr(sanitized)}\n")
    
    # Test 4: Filter validation
    print("4️⃣ Testing filter validation:\n")
    
    test_filters = [
        ({'genre': 'Action'}, "Valid genre filter"),
        ({'year': 2020}, "Valid year filter"),
        ({'year': 1800}, "Invalid year"),
        ({'invalid_key': 'value'}, "Invalid key"),
    ]
    
    for filters, description in test_filters:
        is_valid, error = validator.validate_filters(filters)
        status = "✅" if is_valid else "❌"
        print(f"{status} {description}: {'Valid' if is_valid else error}")
    
    # Test 5: Retry mechanism
    print("\n5️⃣ Testing retry mechanism:\n")
    
    attempt_count = [0]
    
    @retry_on_failure(max_retries=3, delay=0.1, backoff=1.5)
    def flaky_function():
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise Exception(f"Simulated failure {attempt_count[0]}")
        return "Success!"
    
    try:
        result = flaky_function()
        print(f"✅ Function succeeded after {attempt_count[0]} attempts: {result}")
    except Exception as e:
        print(f"❌ Function failed: {e}")
    
    # Test 6: Empty results handling
    print("\n6️⃣ Testing empty results handling:\n")
    response = handler.handle_empty_results("nonexistent movie xyz123")
    print(f"Empty results response:\n{response['answer'][:200]}...")
    
    print("\n" + "="*70)
    print("✅ ERROR HANDLING TEST COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_error_handling()