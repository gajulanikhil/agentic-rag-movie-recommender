"""
Verification for Phase 6: Error Handling
"""

import sys
from error_handler import ErrorHandler, InputValidator
from rag_chain import NetflixGPTRobust


def verify_phase6():
    """Verify all Phase 6 components"""
    
    checks_passed = 0
    total_checks = 8
    
    print("\n" + "="*70)
    print("PHASE 6 VERIFICATION: ERROR HANDLING")
    print("="*70 + "\n")
    
    # Check 1: Error handler module
    print("1️⃣ Testing error handler module...")
    try:
        handler = ErrorHandler()
        validator = InputValidator()
        print("   ✅ Error handler initialized")
        checks_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Check 2: Query validation
    print("\n2️⃣ Testing query validation...")
    try:
        is_valid, _ = handler.validate_query("")
        if not is_valid:  # Should reject empty
            print("   ✅ Empty query rejected")
            checks_passed += 1
        else:
            print("   ❌ Empty query not rejected")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Check 3: Ollama check
    print("\n3️⃣ Testing Ollama connection check...")
    try:
        is_connected, error = handler.check_ollama_connection()
        if is_connected:
            print("   ✅ Ollama connection verified")
            checks_passed += 1
        else:
            print(f"   ⚠️  Ollama not connected: {error}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Check 4: Input sanitization
    print("\n4️⃣ Testing input sanitization...")
    try:
        sanitized = validator.sanitize_query("  test  ")
        if sanitized == "test":
            print("   ✅ Sanitization working")
            checks_passed += 1
        else:
            print(f"   ❌ Unexpected result: {sanitized}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Check 5: Robust RAG initialization
    print("\n5️⃣ Testing robust RAG initialization...")
    try:
        rag = NetflixGPTRobust(
            model_name="llama3.2",
            enable_validation=True
        )
        print("   ✅ Robust RAG initialized")
        checks_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Check 6: Safe query with error
    print("\n6️⃣ Testing safe query with invalid input...")
    try:
        response = rag.query_safe("", raise_on_error=False)
        if not response['success'] and 'error' in response:
            print("   ✅ Error handled gracefully")
            checks_passed += 1
        else:
            print("   ❌ Error not handled properly")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Check 7: Safe query with valid input
    print("\n7️⃣ Testing safe query with valid input...")
    try:
        response = rag.query_safe("Recommend movies", raise_on_error=False)
        if response['success']:
            print("   ✅ Valid query processed")
            checks_passed += 1
        else:
            print(f"   ❌ Valid query failed: {response.get('error')}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Check 8: Health check
    print("\n8️⃣ Testing health check...")
    try:
        health = rag.health_check()
        if 'overall_status' in health and 'checks' in health:
            print(f"   ✅ Health check working (status: {health['overall_status']})")
            checks_passed += 1
        else:
            print("   ❌ Health check incomplete")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Summary
    print("\n" + "="*70)
    print(f"RESULTS: {checks_passed}/{total_checks} checks passed")
    print("="*70)
    
    if checks_passed == total_checks:
        print("\n🎉 Phase 6 complete! Error handling is working.")
        return True
    elif checks_passed >= 6:
        print("\n⚠️  Most checks passed. Review any failures above.")
        return True
    else:
        print("\n❌ Multiple failures. Please review errors.")
        return False


if __name__ == "__main__":
    success = verify_phase6()
    sys.exit(0 if success else 1)