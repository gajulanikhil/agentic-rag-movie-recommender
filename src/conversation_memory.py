"""
Conversation Memory for Netflix GPT
Tracks conversation history and user preferences
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path
from collections import deque


class ConversationMemory:
    """
    Manages conversation history with configurable memory strategies
    """
    
    def __init__(
        self,
        max_turns: int = 5,
        memory_type: str = "buffer",  # "buffer" or "summary"
        persist_path: Optional[str] = None
    ):
        """
        Initialize conversation memory
        
        Args:
            max_turns: Maximum number of conversation turns to remember
            memory_type: Type of memory ("buffer" keeps recent turns, "summary" condenses)
            persist_path: Optional path to save/load conversation
        """
        self.max_turns = max_turns
        self.memory_type = memory_type
        self.persist_path = persist_path
        
        # Store conversation turns
        self.history: deque = deque(maxlen=max_turns)
        
        # Track mentioned movies to avoid repetition
        self.mentioned_movies: set = set()
        
        # Track user preferences
        self.user_preferences = {
            'liked_genres': [],
            'disliked_genres': [],
            'liked_movies': [],
            'disliked_movies': [],
            'preferred_era': None,
            'mood_preferences': []
        }
        
        # Session metadata
        self.session_start = datetime.now()
        self.turn_count = 0
        
    def add_turn(
        self, 
        query: str, 
        response: str, 
        sources: List[Dict] = None,
        metadata: Dict = None
    ):
        """
        Add a conversation turn to memory
        
        Args:
            query: User's question
            response: System's answer
            sources: List of source documents used
            metadata: Additional turn metadata
        """
        turn = {
            'turn_number': self.turn_count + 1,
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response': response,
            'sources': sources or [],
            'metadata': metadata or {}
        }
        
        self.history.append(turn)
        self.turn_count += 1
        
        # Track mentioned movies
        if sources:
            for source in sources:
                title = source.get('title')
                if title:
                    self.mentioned_movies.add(title)
        
        # Extract preferences from conversation
        self._extract_preferences(query, response)
        
    def _extract_preferences(self, query: str, response: str):
        """
        Extract user preferences from conversation
        
        Args:
            query: User's query
            response: System response
        """
        query_lower = query.lower()
        
        # Detect liked genres
        genre_keywords = {
            'action': ['action', 'explosive', 'intense'],
            'comedy': ['funny', 'hilarious', 'laugh'],
            'drama': ['drama', 'emotional', 'moving'],
            'thriller': ['thriller', 'suspense', 'tension'],
            'sci-fi': ['sci-fi', 'science fiction', 'futuristic'],
            'romance': ['romance', 'romantic', 'love story'],
            'horror': ['horror', 'scary', 'frightening']
        }
        
        for genre, keywords in genre_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                if genre not in self.user_preferences['liked_genres']:
                    self.user_preferences['liked_genres'].append(genre)
        
        # Detect dislikes
        dislike_phrases = ["don't like", "not a fan", "dislike", "hate", "avoid"]
        if any(phrase in query_lower for phrase in dislike_phrases):
            for genre, keywords in genre_keywords.items():
                if any(keyword in query_lower for keyword in keywords):
                    if genre not in self.user_preferences['disliked_genres']:
                        self.user_preferences['disliked_genres'].append(genre)
        
        # Detect era preferences
        if '90s' in query_lower or 'nineties' in query_lower:
            self.user_preferences['preferred_era'] = '1990s'
        elif '80s' in query_lower or 'eighties' in query_lower:
            self.user_preferences['preferred_era'] = '1980s'
        elif '2000s' in query_lower:
            self.user_preferences['preferred_era'] = '2000s'
        elif 'recent' in query_lower or 'new' in query_lower or 'latest' in query_lower:
            self.user_preferences['preferred_era'] = 'recent'
        
        # Detect mood preferences
        mood_keywords = {
            'uplifting': ['uplifting', 'feel-good', 'happy', 'cheerful'],
            'intense': ['intense', 'gripping', 'thrilling'],
            'relaxing': ['relaxing', 'calm', 'peaceful', 'cozy'],
            'thought-provoking': ['thought-provoking', 'deep', 'philosophical']
        }
        
        for mood, keywords in mood_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                if mood not in self.user_preferences['mood_preferences']:
                    self.user_preferences['mood_preferences'].append(mood)
    
    def get_context_string(self, include_sources: bool = False) -> str:
        """
        Get conversation history as formatted string
        
        Args:
            include_sources: Whether to include source movies in context
            
        Returns:
            Formatted conversation history
        """
        if not self.history:
            return ""
        
        context_parts = []
        
        for turn in self.history:
            context_parts.append(f"User: {turn['query']}")
            context_parts.append(f"Assistant: {turn['response']}")
            
            if include_sources and turn['sources']:
                movies = [s['title'] for s in turn['sources'][:3]]  # Top 3 only
                context_parts.append(f"(Movies mentioned: {', '.join(movies)})")
            
            context_parts.append("")  # Empty line between turns
        
        return "\n".join(context_parts)
    
    def get_recent_movies(self, n: int = 10) -> List[str]:
        """
        Get recently mentioned movies
        
        Args:
            n: Number of recent movies to return
            
        Returns:
            List of movie titles
        """
        recent_movies = []
        
        # Iterate through history in reverse (most recent first)
        for turn in reversed(self.history):
            if turn['sources']:
                for source in turn['sources']:
                    title = source.get('title')
                    if title and title not in recent_movies:
                        recent_movies.append(title)
                    
                    if len(recent_movies) >= n:
                        return recent_movies
        
        return recent_movies
    
    def is_follow_up_question(self, query: str) -> bool:
        """
        Detect if current query is a follow-up to previous conversation
        
        Args:
            query: Current user query
            
        Returns:
            True if it's a follow-up question
        """
        if not self.history:
            return False
        
        query_lower = query.lower()
        
        # Follow-up indicators
        follow_up_phrases = [
            'that movie', 'that one', 'the one you mentioned',
            'tell me more', 'what about', 'similar to',
            'like that', 'those movies', 'these movies',
            'it', 'them', 'also', 'another', 'more like'
        ]
        
        # Pronouns and references
        reference_words = [
            'it', 'that', 'this', 'those', 'these',
            'same', 'similar'
        ]
        
        # Check for follow-up phrases
        if any(phrase in query_lower for phrase in follow_up_phrases):
            return True
        
        # Check for questions starting with reference words
        query_words = query_lower.split()
        if query_words and query_words[0] in reference_words:
            return True
        
        return False
    
    def enhance_query_with_context(self, query: str) -> str:
        """
        Enhance query with conversation context for better understanding
        
        Args:
            query: Original user query
            
        Returns:
            Enhanced query with context
        """
        if not self.is_follow_up_question(query):
            return query
        
        # Get last turn
        last_turn = self.history[-1] if self.history else None
        
        if not last_turn:
            return query
        
        # Get movies from last response
        recent_movies = []
        if last_turn['sources']:
            recent_movies = [s['title'] for s in last_turn['sources'][:3]]
        
        # Enhance query with context
        if recent_movies:
            context_addition = f" (Previous context: discussing {', '.join(recent_movies)})"
            enhanced = query + context_addition
            return enhanced
        
        return query
    
    def get_preference_summary(self) -> str:
        """
        Get summary of user preferences
        
        Returns:
            Formatted preference summary
        """
        parts = []
        
        if self.user_preferences['liked_genres']:
            parts.append(f"Likes: {', '.join(self.user_preferences['liked_genres'])}")
        
        if self.user_preferences['disliked_genres']:
            parts.append(f"Dislikes: {', '.join(self.user_preferences['disliked_genres'])}")
        
        if self.user_preferences['preferred_era']:
            parts.append(f"Era preference: {self.user_preferences['preferred_era']}")
        
        if self.user_preferences['mood_preferences']:
            parts.append(f"Mood: {', '.join(self.user_preferences['mood_preferences'])}")
        
        return "; ".join(parts) if parts else "No preferences detected yet"
    
    def clear(self):
        """Clear conversation history and preferences"""
        self.history.clear()
        self.mentioned_movies.clear()
        self.user_preferences = {
            'liked_genres': [],
            'disliked_genres': [],
            'liked_movies': [],
            'disliked_movies': [],
            'preferred_era': None,
            'mood_preferences': []
        }
        self.turn_count = 0
        self.session_start = datetime.now()
    
    def save(self, filepath: Optional[str] = None):
        """
        Save conversation to JSON file
        
        Args:
            filepath: Path to save file (uses persist_path if not provided)
        """
        if filepath is None:
            if self.persist_path is None:
                raise ValueError("No filepath provided and no persist_path set")
            filepath = self.persist_path
        
        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'session_start': self.session_start.isoformat(),
            'turn_count': self.turn_count,
            'history': list(self.history),
            'mentioned_movies': list(self.mentioned_movies),
            'user_preferences': self.user_preferences
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Conversation saved to: {filepath}")
    
    def load(self, filepath: Optional[str] = None):
        """
        Load conversation from JSON file
        
        Args:
            filepath: Path to load from (uses persist_path if not provided)
        """
        if filepath is None:
            if self.persist_path is None:
                raise ValueError("No filepath provided and no persist_path set")
            filepath = self.persist_path
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.session_start = datetime.fromisoformat(data['session_start'])
        self.turn_count = data['turn_count']
        self.history = deque(data['history'], maxlen=self.max_turns)
        self.mentioned_movies = set(data['mentioned_movies'])
        self.user_preferences = data['user_preferences']
        
        print(f"📂 Conversation loaded from: {filepath}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        return {
            'session_duration': str(datetime.now() - self.session_start),
            'total_turns': self.turn_count,
            'turns_in_memory': len(self.history),
            'movies_mentioned': len(self.mentioned_movies),
            'preferences': self.get_preference_summary()
        }


# Example usage and testing
def test_conversation_memory():
    """Test conversation memory functionality"""
    
    print("\n" + "="*70)
    print("TESTING CONVERSATION MEMORY")
    print("="*70 + "\n")
    
    # Initialize memory
    memory = ConversationMemory(max_turns=5)
    
    # Simulate conversation
    print("1️⃣ Adding conversation turns...\n")
    
    turns = [
        {
            'query': 'I love action movies. Recommend something exciting!',
            'response': 'I recommend The Dark Knight and Mad Max: Fury Road. Both are intense action films.',
            'sources': [
                {'title': 'The Dark Knight', 'year': 2008, 'genres': ['Action', 'Crime']},
                {'title': 'Mad Max: Fury Road', 'year': 2015, 'genres': ['Action', 'Sci-Fi']}
            ]
        },
        {
            'query': 'Tell me more about that first movie',
            'response': 'The Dark Knight is a 2008 superhero film directed by Christopher Nolan...',
            'sources': [
                {'title': 'The Dark Knight', 'year': 2008, 'genres': ['Action', 'Crime']}
            ]
        },
        {
            'query': 'What about something similar but more recent?',
            'response': 'For recent action films similar to The Dark Knight, I suggest John Wick...',
            'sources': [
                {'title': 'John Wick', 'year': 2014, 'genres': ['Action', 'Thriller']}
            ]
        }
    ]
    
    for turn in turns:
        memory.add_turn(
            query=turn['query'],
            response=turn['response'],
            sources=turn['sources']
        )
        print(f"Turn {memory.turn_count}:")
        print(f"  User: {turn['query']}")
        print(f"  Is follow-up: {memory.is_follow_up_question(turn['query'])}")
        print()
    
    # Test context retrieval
    print("\n2️⃣ Conversation context:\n")
    context = memory.get_context_string(include_sources=True)
    print(context)
    
    # Test recent movies
    print("\n3️⃣ Recently mentioned movies:")
    recent = memory.get_recent_movies(n=5)
    for i, movie in enumerate(recent, 1):
        print(f"  {i}. {movie}")
    
    # Test preferences
    print("\n4️⃣ User preferences:")
    print(f"  {memory.get_preference_summary()}")
    
    # Test follow-up detection
    print("\n5️⃣ Follow-up question detection:")
    test_queries = [
        "What about that movie?",
        "Tell me more about it",
        "Recommend horror movies",  # Not a follow-up
        "Similar to those",
    ]
    
    for query in test_queries:
        is_followup = memory.is_follow_up_question(query)
        print(f"  '{query}' → {'Follow-up' if is_followup else 'New topic'}")
    
    # Test enhancement
    print("\n6️⃣ Query enhancement:")
    test_query = "What about that one?"
    enhanced = memory.enhance_query_with_context(test_query)
    print(f"  Original: {test_query}")
    print(f"  Enhanced: {enhanced}")
    
    # Test summary
    print("\n7️⃣ Conversation summary:")
    summary = memory.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Test save/load
    print("\n8️⃣ Testing save/load...")
    save_path = "data/conversations/test_memory.json"
    memory.save(save_path)
    
    # Create new memory and load
    new_memory = ConversationMemory()
    new_memory.load(save_path)
    print(f"  Loaded {len(new_memory.history)} turns")
    print(f"  Loaded {len(new_memory.mentioned_movies)} movies")
    
    print("\n" + "="*70)
    print("✅ CONVERSATION MEMORY TEST COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_conversation_memory()