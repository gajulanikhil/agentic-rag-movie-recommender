"""
Utility functions for Netflix GPT RAG system
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def save_conversation(conversation: List[Dict], filename: str = None):
    """
    Save conversation history to JSON file
    
    Args:
        conversation: List of question-answer pairs
        filename: Output filename (auto-generated if None)
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.json"
    
    output_dir = Path("data/conversations")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = output_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(conversation, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Conversation saved to: {filepath}")
    return filepath


def load_conversation(filename: str) -> List[Dict]:
    """Load conversation history from JSON file"""
    filepath = Path("data/conversations") / filename
    
    if not filepath.exists():
        raise FileNotFoundError(f"Conversation file not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        conversation = json.load(f)
    
    return conversation


def format_conversation_history(conversation: List[Dict]) -> str:
    """
    Format conversation history as readable text
    
    Args:
        conversation: List of Q&A dictionaries
        
    Returns:
        Formatted string
    """
    lines = []
    lines.append("="*70)
    lines.append("CONVERSATION HISTORY")
    lines.append("="*70 + "\n")
    
    for i, turn in enumerate(conversation, 1):
        lines.append(f"Turn {i}:")
        lines.append(f"Q: {turn['question']}")
        lines.append(f"A: {turn['answer']}\n")
        
        if turn.get('sources'):
            sources = [s['title'] for s in turn['sources']]
            lines.append(f"Sources: {', '.join(sources)}\n")
        
        lines.append("-"*70 + "\n")
    
    return "\n".join(lines)


def extract_movie_titles(response: Dict) -> List[str]:
    """
    Extract movie titles mentioned in the response
    
    Args:
        response: RAG response dictionary
        
    Returns:
        List of movie titles
    """
    titles = []
    
    # From sources
    if response.get('sources'):
        titles.extend([s['title'] for s in response['sources']])
    
    # Could add NLP extraction from answer text here
    # For now, just return source titles
    
    return list(set(titles))  # Remove duplicates


def calculate_query_statistics(responses: List[Dict]) -> Dict[str, Any]:
    """
    Calculate statistics from multiple responses
    
    Args:
        responses: List of response dictionaries
        
    Returns:
        Statistics dictionary
    """
    stats = {
        'total_queries': len(responses),
        'total_sources_retrieved': 0,
        'unique_movies': set(),
        'genres_mentioned': {},
        'avg_sources_per_query': 0
    }
    
    for response in responses:
        if response.get('sources'):
            stats['total_sources_retrieved'] += len(response['sources'])
            
            for source in response['sources']:
                stats['unique_movies'].add(source['title'])
                
                genres = source.get('genres', [])
                if isinstance(genres, list):
                    for genre in genres:
                        stats['genres_mentioned'][genre] = stats['genres_mentioned'].get(genre, 0) + 1
    
    if stats['total_queries'] > 0:
        stats['avg_sources_per_query'] = stats['total_sources_retrieved'] / stats['total_queries']
    
    stats['unique_movies'] = list(stats['unique_movies'])
    
    return stats


def print_statistics(stats: Dict):
    """Pretty print statistics"""
    print("\n" + "="*70)
    print("QUERY STATISTICS")
    print("="*70 + "\n")
    
    print(f"Total Queries: {stats['total_queries']}")
    print(f"Total Sources Retrieved: {stats['total_sources_retrieved']}")
    print(f"Unique Movies Mentioned: {len(stats['unique_movies'])}")
    print(f"Avg Sources per Query: {stats['avg_sources_per_query']:.2f}\n")
    
    if stats['genres_mentioned']:
        print("Top Genres Mentioned:")
        sorted_genres = sorted(
            stats['genres_mentioned'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        for genre, count in sorted_genres[:5]:
            print(f"  {genre}: {count}")
    
    print("\n" + "="*70 + "\n")


# Example usage function
def demo_utils():
    """Demonstrate utility functions"""
    from rag_chain import NetflixGPTRAG
    
    # Initialize RAG
    rag = NetflixGPTRAG()
    
    # Run some queries
    queries = [
        "Recommend action movies",
        "Best comedies",
        "Thriller films"
    ]
    
    conversation = []
    responses = []
    
    for query in queries:
        response = rag.query(query)
        responses.append(response)
        
        conversation.append({
            'question': response['question'],
            'answer': response['answer'],
            'sources': response.get('sources', []),
            'timestamp': response['timestamp']
        })
    
    # Save conversation
    save_conversation(conversation)
    
    # Print formatted history
    print(format_conversation_history(conversation))
    
    # Calculate and print statistics
    stats = calculate_query_statistics(responses)
    print_statistics(stats)


if __name__ == "__main__":
    demo_utils()