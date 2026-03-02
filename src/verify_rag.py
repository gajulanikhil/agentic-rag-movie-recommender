"""
Verification script for RAG pipeline
"""

from rag_chain import NetflixGPTRAG
import sys


def verify_rag_pipeline():
    """Verify RAG pipeline is working correctly"""
    
    checks_passed = 0
    total_checks = 6
    
    print("\n" + "="*70)
    print("RAG PIPELINE VERIFICATION")
    print("="*70 + "\n")
    
    # Check 1: Initialize RAG system
    print("1️⃣ Initializing RAG system...")
    try:
        rag = NetflixGPTRAG(model_name="llama3.2", temperature=0.7)
        print("   ✅ RAG system initialized")
        checks_passed += 1
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        return False
    
    # Check 2: Test vector store connection
    print("\n2️⃣ Testing vector store connection...")
    try:
        count = rag.vector_store.collection.count()
        if count > 0:
            print(f"   ✅ Vector store connected ({count} chunks)")
            checks_passed += 1
        else:
            print("   ❌ Vector store is empty")
    except Exception as e:
        print(f"   ❌ Vector store error: {e}")
    
    # Check 3: Test retrieval
    print("\n3️⃣ Testing document retrieval...")
    try:
        results = rag.retrieve_context("action movies")
        if results['documents']:
            print(f"   ✅ Retrieved {len(results['documents'])} documents")
            checks_passed += 1
        else:
            print("   ❌ No documents retrieved")
    except Exception as e:
        print(f"   ❌ Retrieval failed: {e}")
    
    # Check 4: Test LLM connection
    print("\n4️⃣ Testing LLM connection...")
    try:
        test_response = rag.llm.invoke("Say 'test successful'")
        if test_response:
            print("   ✅ LLM responding")
            checks_passed += 1
        else:
            print("   ❌ LLM not responding")
    except Exception as e:
        print(f"   ❌ LLM error: {e}")
        print("   💡 Make sure Ollama is running: `ollama serve`")
    
    # Check 5: Test full RAG query
    print("\n5️⃣ Testing full RAG query...")
    try:
        response = rag.query("Recommend a movie", return_sources=True)
        if response['answer'] and response['sources']:
            print("   ✅ Full query successful")
            print(f"   Answer length: {len(response['answer'])} chars")
            print(f"   Sources returned: {len(response['sources'])}")
            checks_passed += 1
        else:
            print("   ❌ Query returned incomplete response")
    except Exception as e:
        print(f"   ❌ Query failed: {e}")
    
    # Check 6: Test response quality
    print("\n6️⃣ Testing response quality...")
    try:
        response = rag.query("What's a good thriller movie?")
        answer = response['answer'].lower()
        
        # Check if answer mentions movies
        has_content = len(answer) > 50
        mentions_movie = any(keyword in answer for keyword in ['movie', 'film', 'watch', 'recommend'])
        
        if has_content and mentions_movie:
            print("   ✅ Response quality acceptable")
            checks_passed += 1
        else:
            print("   ⚠️  Response may need improvement")
            print(f"      Length: {len(answer)} chars")
            print(f"      Mentions movies: {mentions_movie}")
    except Exception as e:
        print(f"   ❌ Quality check failed: {e}")
    
    # Summary
    print("\n" + "="*70)
    print(f"RESULTS: {checks_passed}/{total_checks} checks passed")
    print("="*70)
    
    if checks_passed == total_checks:
        print("\n🎉 All checks passed! RAG pipeline is ready.")
        return True
    elif checks_passed >= 4:
        print("\n⚠️  Most checks passed. System functional but may need tuning.")
        return True
    else:
        print("\n❌ Multiple checks failed. Please review errors above.")
        return False


if __name__ == "__main__":
    success = verify_rag_pipeline()
    sys.exit(0 if success else 1)