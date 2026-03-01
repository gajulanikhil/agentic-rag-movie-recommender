"""
Verification script for vector store setup
Run this to ensure everything is working correctly
"""

from vectorstore import MovieVectorStore
from pathlib import Path
import sys

def verify_vectorstore():
    """Verify vector store is properly set up"""
    
    checks_passed = 0
    total_checks = 5
    
    print("\n" + "="*60)
    print("VECTOR STORE VERIFICATION")
    print("="*60 + "\n")
    
    # Check 1: Persistence directory exists
    print("1️⃣ Checking persistence directory...")
    persist_dir = Path("data/vectorstore")
    if persist_dir.exists():
        print("   ✅ Directory exists")
        checks_passed += 1
    else:
        print("   ❌ Directory not found")
        return False
    
    # Check 2: Load vector store
    print("\n2️⃣ Loading vector store...")
    try:
        vector_store = MovieVectorStore()
        vector_store.collection = vector_store.client.get_collection("netflix_gpt_movies")
        print("   ✅ Vector store loaded successfully")
        checks_passed += 1
    except Exception as e:
        print(f"   ❌ Failed to load: {e}")
        return False
    
    # Check 3: Check document count
    print("\n3️⃣ Checking document count...")
    stats = vector_store.get_collection_stats()
    chunk_count = stats['total_chunks']
    if chunk_count >= 10:  # Should have at least 10 chunks
        print(f"   ✅ Found {chunk_count} chunks (minimum 10 required)")
        checks_passed += 1
    else:
        print(f"   ❌ Only {chunk_count} chunks found (need at least 10)")
    
    # Check 4: Test retrieval
    print("\n4️⃣ Testing retrieval...")
    try:
        results = vector_store.search("action movies", n_results=3)
        if results['documents'][0]:
            print(f"   ✅ Retrieved {len(results['documents'][0])} results")
            checks_passed += 1
        else:
            print("   ❌ No results returned")
    except Exception as e:
        print(f"   ❌ Retrieval failed: {e}")
    
    # Check 5: Test metadata
    print("\n5️⃣ Checking metadata structure...")
    try:
        results = vector_store.search("movies", n_results=1)
        if results['metadatas'][0]:
            metadata = results['metadatas'][0][0]
            required_fields = ['title', 'genres']
            has_fields = all(field in metadata for field in required_fields)
            if has_fields:
                print(f"   ✅ Metadata structure correct")
                print(f"      Sample: {metadata.get('title', 'N/A')}")
                checks_passed += 1
            else:
                print(f"   ❌ Missing required metadata fields")
    except Exception as e:
        print(f"   ❌ Metadata check failed: {e}")
    
    # Summary
    print("\n" + "="*60)
    print(f"RESULTS: {checks_passed}/{total_checks} checks passed")
    print("="*60)
    
    if checks_passed == total_checks:
        print("\n🎉 All checks passed! Vector store is ready.")
        print("\n📊 Collection Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        return True
    else:
        print("\n⚠️  Some checks failed. Please review the output above.")
        return False

if __name__ == "__main__":
    success = verify_vectorstore()
    sys.exit(0 if success else 1)