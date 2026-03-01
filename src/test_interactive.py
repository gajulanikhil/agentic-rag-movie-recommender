"""
Interactive testing script for RAG system
"""

from rag_chain import NetflixGPTRAG, MovieQueryHelper
import sys

def print_response(response):
    """Pretty print a response"""
    print("\n" + "="*70)
    print("🎬 NETFLIX GPT RESPONSE")
    print("="*70 + "\n")
    
    print(f"❓ Your Question:\n{response['question']}\n")
    print(f"💡 Answer:\n{response['answer']}\n")
    
    if response.get('sources'):
        print(f"📚 Based on {len(response['sources'])} movies in our database:")
        for i, source in enumerate(response['sources'], 1):
            genres = source.get('genres', [])
            if isinstance(genres, list):
                genres_str = ', '.join(genres)
            else:
                genres_str = str(genres)
            
            print(f"  {i}. {source['title']} ({source['year']})")
            print(f"     Genres: {genres_str}")
            print(f"     Relevance: {source['similarity_score']:.0%}\n")
    
    print("="*70 + "\n")


def interactive_mode():
    """Run interactive query mode"""
    
    print("\n" + "🎬"*35)
    print("\n   NETFLIX GPT - Interactive Movie Recommendation System\n")
    print("🎬"*35 + "\n")
    
    # Initialize RAG
    print("Initializing system... (this may take a moment)\n")
    rag = NetflixGPTRAG(model_name="llama3.2")
    
    print("✅ System ready! Type your movie questions below.")
    print("   Examples:")
    print("   - 'Recommend action movies'")
    print("   - 'I want something funny'")
    print("   - 'Movies like Inception'")
    print("   - 'Best dramas from the 90s'\n")
    print("Type 'quit' or 'exit' to stop.\n")
    print("-"*70 + "\n")
    
    # Query loop
    while True:
        try:
            # Get user input
            query = input("🎥 Your question: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thanks for using Netflix GPT!\n")
                break
            
            # Process query
            response = rag.query(query)
            
            # Display response
            print_response(response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            print("Please try again or type 'quit' to exit.\n")


def quick_test():
    """Run quick predefined tests"""
    
    print("\n🚀 QUICK TEST MODE\n")
    
    rag = NetflixGPTRAG(model_name="llama3.2")
    
    queries = [
        "Recommend a thriller movie",
        "What's a good comedy for family movie night?",
        "I love sci-fi movies. What should I watch?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}/{len(queries)}")
        print(f"{'='*70}")
        
        response = rag.query(query)
        print_response(response)
        
        if i < len(queries):
            input("Press Enter for next test...")
    
    print("\n✅ Quick test complete!\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_test()
    else:
        interactive_mode()