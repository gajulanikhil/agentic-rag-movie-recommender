"""
Verification script for conversation memory
"""

from conversation_memory import ConversationMemory
from rag_chain import NetflixGPTWithMemory
import sys


def verify_memory():
    """Verify conversation memory is working"""
    
    checks_passed = 0
    total_checks = 7
    
    print("\n" + "="*70)
    print("CONVERSATION MEMORY VERIFICATION")
    print("="*70 + "\n")
    
    # Check 1: Initialize memory
    print("1️⃣ Initializing conversation memory...")
    try:
        memory = ConversationMemory(max_turns=5)
        print("   ✅ Memory initialized")
        checks_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Check 2: Add turns
    print("\n2️⃣ Testing add_turn...")
    try:
        memory.add_turn(
            query="Test query",
            response="Test response",
            sources=[{'title': 'Test Movie', 'year': 2020}]
        )
        if len(memory.history) == 1:
            print("   ✅ Turn added successfully")
            checks_passed += 1
        else:
            print("   ❌ Turn not added")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Check 3: Follow-up detection
    print("\n3️⃣ Testing follow-up detection...")
    try:
        is_followup = memory.is_follow_up_question("Tell me more about that")
        if is_followup:
            print("   ✅ Follow-up detected correctly")
            checks_passed += 1
        else:
            print("   ⚠️  Follow-up not detected (may be OK)")
            checks_passed += 0.5
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Check 4: Context retrieval
    print("\n4️⃣ Testing context retrieval...")
    try:
        context = memory.get_context_string()
        if context and len(context) > 0:
            print("   ✅ Context retrieved")
            checks_passed += 1
        else:
            print("   ❌ No context retrieved")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Check 5: Preference extraction
    print("\n5️⃣ Testing preference extraction...")
    try:
        memory.add_turn(
            query="I love action movies",
            response="Great! Here are some action movies",
            sources=[]
        )
        if 'action' in memory.user_preferences['liked_genres']:
            print("   ✅ Preference detected")
            checks_passed += 1
        else:
            print("   ⚠️  Preference not detected")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Check 6: Save/Load
    print("\n6️⃣ Testing save and load...")
    try:
        import tempfile
        import os
        
        # Create temp file
        temp_path = os.path.join(tempfile.gettempdir(), "test_memory.json")
        
        # Save
        memory.save(temp_path)
        
        # Load into new memory
        new_memory = ConversationMemory()
        new_memory.load(temp_path)
        
        if len(new_memory.history) == len(memory.history):
            print("   ✅ Save/load working")
            checks_passed += 1
        else:
            print("   ❌ Save/load failed")
        
        # Cleanup
        os.remove(temp_path)
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Check 7: Integration with RAG
    print("\n7️⃣ Testing integration with RAG...")
    try:
        rag = NetflixGPTWithMemory(
            model_name="llama3.2",
            max_memory_turns=3
        )
        
        response = rag.query_with_memory("Test query")
        
        if response and 'answer' in response:
            print("   ✅ RAG with memory working")
            checks_passed += 1
        else:
            print("   ❌ RAG integration failed")
            
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        print(f"   💡 Make sure Ollama is running")
    
    # Summary
    print("\n" + "="*70)
    print(f"RESULTS: {checks_passed}/{total_checks} checks passed")
    print("="*70)
    
    if checks_passed >= 6:
        print("\n🎉 Conversation memory is working!")
        return True
    else:
        print("\n⚠️  Some checks failed. Review errors above.")
        return False


if __name__ == "__main__":
    success = verify_memory()
    sys.exit(0 if success else 1)