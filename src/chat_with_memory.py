"""
Interactive chat interface with robust error handling
"""

from rag_chain import NetflixGPTRobust
from error_handler import ErrorHandler
from datetime import datetime
import sys


def print_separator(char="=", length=70):
    """Print a separator line"""
    print(char * length)


def print_response(response):
    """Pretty print response with error handling"""
    
    if not response.get('success', True):
        # Error response
        print(f"\n⚠️  {response['answer']}\n")
        
        if response.get('suggestions'):
            print("💡 Suggestions:")
            for suggestion in response['suggestions']:
                print(f"  • {suggestion}")
            print()
        return
    
    # Normal response
    print(f"\n💡 Netflix GPT:")
    print(f"{response['answer']}\n")
    
    if response.get('sources'):
        print(f"📚 Based on:")
        for i, source in enumerate(response['sources'][:3], 1):
            print(f"  {i}. {source['title']} ({source['year']})")
        print()


def main():
    """Main interactive chat loop with error handling"""
    
    print("\n" + "🎬"*35)
    print("\n   NETFLIX GPT - Robust Chat System")
    print("   Your AI Movie Recommendation Assistant\n")
    print("🎬"*35 + "\n")
    
    # Generate session ID
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Initialize RAG with error handling
    print("🔧 Initializing system...\n")
    
    try:
        rag = NetflixGPTRobust(
            model_name="llama3.2",
            temperature=0.7,
            max_memory_turns=5,
            session_id=session_id,
            enable_validation=True
        )
        
        # Perform health check
        print("🏥 Running health check...")
        health = rag.health_check()
        
        if health['overall_status'] == 'unhealthy':
            print("\n⚠️  System health check failed:")
            for component, status in health['checks'].items():
                if status['status'] == 'error':
                    print(f"   ❌ {component}: {status['message']}")
            print("\nPlease fix the issues above before continuing.\n")
            sys.exit(1)
        
        print("✅ System healthy and ready!\n")
        
    except Exception as e:
        print(f"\n❌ Failed to initialize system: {e}\n")
        print("Please check:")
        print("  1. Ollama is running: 'ollama serve'")
        print("  2. Model is available: 'ollama list'")
        print("  3. Vector store is set up: 'python src/vectorstore.py'\n")
        sys.exit(1)
    
    print("💬 I remember our conversation and handle errors gracefully.")
    print("   Try asking things like:")
    print("   - 'Recommend action movies'")
    print("   - 'Tell me more about that'")
    print("   - 'What about comedies?'\n")
    
    print("Commands:")
    print("  'health' - Check system health")
    print("  'memory' - Show conversation summary")
    print("  'clear' - Clear conversation history")
    print("  'save' - Save conversation")
    print("  'quit' - Exit\n")
    print_separator("-")
    print()
    
    # Chat loop
    error_count = 0
    max_consecutive_errors = 3
    
    while True:
        try:
            # Get input
            user_input = input("🎥 You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n💾 Saving conversation...")
                try:
                    rag.save_conversation()
                    print("✅ Conversation saved")
                except Exception as e:
                    print(f"⚠️  Could not save: {e}")
                print("👋 Thanks for chatting! Goodbye!\n")
                break
            
            elif user_input.lower() == 'health':
                health = rag.health_check()
                print(f"\n🏥 System Health: {health['overall_status'].upper()}")
                print_separator("-")
                for component, status in health['checks'].items():
                    icon = "✅" if status['status'] == 'ok' else "❌"
                    print(f"{icon} {component}: {status['message']}")
                print_separator("-")
                print()
                continue
            
            elif user_input.lower() == 'memory':
                print("\n📊 Conversation Summary:")
                print_separator("-")
                summary = rag.get_memory_summary()
                for key, value in summary.items():
                    print(f"{key}: {value}")
                print_separator("-")
                print()
                continue
            
            elif user_input.lower() == 'clear':
                rag.clear_memory()
                error_count = 0
                print("🗑️  Conversation cleared. Starting fresh!\n")
                continue
            
            elif user_input.lower() == 'save':
                try:
                    rag.save_conversation()
                    print("✅ Conversation saved\n")
                except Exception as e:
                    print(f"⚠️  Could not save: {e}\n")
                continue
            
            # Process query with error handling
            response = rag.query_safe(user_input, raise_on_error=False)
            
            # Track errors
            if not response.get('success', True):
                error_count += 1
                if error_count >= max_consecutive_errors:
                    print(f"\n⚠️  Multiple errors occurred ({error_count} in a row).")
                    print("Type 'health' to check system status or 'quit' to exit.\n")
            else:
                error_count = 0  # Reset on success
            
            # Show if it's a follow-up
            if response.get('is_followup'):
                print("🔗 (I understood this as a follow-up question)")
            
            # Display response
            print_response(response)
            
            print_separator("-")
            print()
            
        except KeyboardInterrupt:
            print("\n\n💾 Saving conversation...")
            try:
                rag.save_conversation()
            except:
                pass
            print("👋 Interrupted. Goodbye!\n")
            break
        
        except Exception as e:
            error_count += 1
            print(f"\n❌ Unexpected error: {e}\n")
            
            if error_count >= max_consecutive_errors:
                print("⚠️  Too many errors. Please restart the application.\n")
                break
            
            print("Let's try again!\n")


if __name__ == "__main__":
    main()