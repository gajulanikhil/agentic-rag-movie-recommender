"""
Comprehensive test suite for error handling
"""

from rag_chain import NetflixGPTRobust
from error_handler import ErrorHandler, InputValidator
from vectorstore import MovieVectorStore
import sys
import time


def run_test(test_name: str, test_func):
    """Run a single test with error handling"""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print('='*70 + "\n")
    
    try:
        start = time.time()
        result = test_func()
        elapsed = time.time() - start
        
        if result:
            print(f"\n✅ PASSED ({elapsed:.2f}s)")
        else:
            print(f"\n❌ FAILED ({elapsed:.2f}s)")
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_validation():
    """Test query validation"""
    handler = ErrorHandler()
    
    test_cases = [
        ("", False, "Empty query"),
        ("hi", False, "Too short"),
        ("a" * 600, False, "Too long"),
        ("!@#$", False, "Special chars only"),
        ("Recommend movies", True, "Valid query"),
        ("What are good action movies?", True, "Valid question"),
    ]
    
    passed = 0
    for query, should_pass, description in test_cases:
        is_valid, error = handler.validate_query(query)
        
        if is_valid == should_pass:
            print(f"✅ {description}")
            passed += 1
        else:
            print(f"❌ {description}: Expected {should_pass}, got {is_valid}")
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_ollama_connection():
    """Test Ollama connection check"""
    handler = ErrorHandler()
    
    is_connected, error = handler.check_ollama_connection()
    
    if is_connected:
        print("✅ Ollama is running")
        return True
    else:
        print(f"❌ Ollama connection failed:\n{error}")
        return False


def test_vector_store_validation():
    """Test vector store validation"""
    handler = ErrorHandler()
    
    try:
        vector_store = MovieVectorStore()
        vector_store.collection = vector_store.client.get_collection("netflix_gpt_movies")
        
        is_valid, error = handler.validate_vector_store(vector_store)
        
        if is_valid:
            count = vector_store.collection.count()
            print(f"✅ Vector store valid ({count} chunks)")
            return True
        else:
            print(f"❌ Vector store invalid: {error}")
            return False
            
    except Exception as e:
        print(f"❌ Could not load vector store: {e}")
        return False


def test_input_sanitization():
    """Test input sanitization"""
    validator = InputValidator()
    
    test_cases = [
        ("  spaces  ", "spaces"),
        ("multiple\n\nlines", "multiple lines"),
        ("UPPERCASE", "UPPERCASE"),
        ("  Mixed   Case  ", "Mixed Case"),
    ]
    
    passed = 0
    for input_text, expected_contains in test_cases:
        sanitized = validator.sanitize_query(input_text)
        
        if expected_contains in sanitized:
            print(f"✅ Sanitized: {repr(input_text)} → {repr(sanitized)}")
            passed += 1
        else:
            print(f"❌ Sanitization failed for {repr(input_text)}")
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_empty_results_handling():
    """Test handling of empty results"""
    handler = ErrorHandler()
    
    response = handler.handle_empty_results("nonexistent query xyz123")
    
    has_answer = 'answer' in response and len(response['answer']) > 0
    has_suggestions = 'suggestions' in response and len(response['suggestions']) > 0
    
    if has_answer and has_suggestions:
        print("✅ Empty results handled correctly")
        print(f"   Suggestions provided: {len(response['suggestions'])}")
        return True
    else:
        print("❌ Empty results not handled properly")
        return False


def test_error_responses():
    """Test error responses from RAG system"""
    
    try:
        rag = NetflixGPTRobust(
            model_name="llama3.2",
            enable_validation=True
        )
        
        # Test empty query
        response1 = rag.query_safe("", raise_on_error=False)
        empty_handled = not response1['success'] and 'error' in response1
        
        # Test too short query
        response2 = rag.query_safe("hi", raise_on_error=False)
        short_handled = not response2['success'] and 'error' in response2
        
        # Test valid query
        response3 = rag.query_safe("Recommend movies", raise_on_error=False)
        valid_handled = response3['success']
        
        results = [
            ("Empty query error", empty_handled),
            ("Short query error", short_handled),
            ("Valid query success", valid_handled),
        ]
        
        passed = 0
        for description, result in results:
            if result:
                print(f"✅ {description}")
                passed += 1
            else:
                print(f"❌ {description}")
        
        print(f"\nPassed: {passed}/{len(results)}")
        return passed == len(results)
        
    except Exception as e:
        print(f"❌ Could not initialize RAG: {e}")
        return False


def test_batch_processing():
    """Test batch query processing with errors"""
    
    try:
        rag = NetflixGPTRobust(
            model_name="llama3.2",
            enable_validation=True
        )
        
        queries = [
            "Good action movies",
            "",  # Invalid
            "Thriller recommendations",
            "xyz",  # Too short
            "Comedy movies",
        ]
        
        responses = rag.batch_query_safe(queries, stop_on_error=False)
        
        if len(responses) == len(queries):
            success_count = sum(1 for r in responses if r.get('success', False))
            error_count = len(responses) - success_count
            
            print(f"✅ Processed {len(queries)} queries")
            print(f"   Successful: {success_count}")
            print(f"   Errors: {error_count}")
            
            return error_count >= 2  # Should have at least 2 errors
        else:
            print(f"❌ Expected {len(queries)} responses, got {len(responses)}")
            return False
            
    except Exception as e:
        print(f"❌ Batch processing failed: {e}")
        return False


def test_health_check():
    """Test system health check"""
    
    try:
        rag = NetflixGPTRobust(
            model_name="llama3.2",
            enable_validation=True
        )
        
        health = rag.health_check()
        
        has_status = 'overall_status' in health
        has_checks = 'checks' in health
        has_ollama = 'ollama' in health.get('checks', {})
        has_vector = 'vector_store' in health.get('checks', {})
        
        results = [
            ("Has overall status", has_status),
            ("Has checks", has_checks),
            ("Checks Ollama", has_ollama),
            ("Checks vector store", has_vector),
        ]
        
        passed = sum(1 for _, result in results if result)
        
        for description, result in results:
            icon = "✅" if result else "❌"
            print(f"{icon} {description}")
        
        print(f"\nOverall status: {health['overall_status']}")
        print(f"Passed: {passed}/{len(results)}")
        
        return passed == len(results)
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def main():
    """Run all tests"""
    
    print("\n" + "🎬"*35)
    print("\n   ERROR HANDLING TEST SUITE")
    print("\n" + "🎬"*35)
    
    tests = [
        ("Query Validation", test_query_validation),
        ("Ollama Connection", test_ollama_connection),
        ("Vector Store Validation", test_vector_store_validation),
        ("Input Sanitization", test_input_sanitization),
        ("Empty Results Handling", test_empty_results_handling),
        ("Error Responses", test_error_responses),
        ("Batch Processing", test_batch_processing),
        ("Health Check", test_health_check),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = run_test(test_name, test_func)
        results.append((test_name, result))
        time.sleep(0.5)  # Brief pause between tests
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        icon = "✅" if result else "❌"
        print(f"{icon} {test_name}")
    
    print(f"\n{'='*70}")
    print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)