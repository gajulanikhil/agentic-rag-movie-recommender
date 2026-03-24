"""
RAG Chain for Movie Recommender
Combines retrieval + LLM generation for movie recommendations
"""

from typing import List, Dict, Any, Optional
import json
import requests
from datetime import datetime
from conversation_memory import ConversationMemory

# LangChain imports
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import Document

# Our vector store
from vectorstore import MovieVectorStore

from error_handler import (
    ErrorHandler, 
    InputValidator, 
    retry_on_failure,
    OllamaConnectionError,
    VectorStoreError,
    QueryValidationError,
    NoResultsError
)

class NetflixGPTRAG:
    """
    RAG system for movie recommendations
    """
    
    def __init__(
        self,
        vector_store: MovieVectorStore = None,
        model_name: str = "llama3.2",
        temperature: float = 0.7,
        top_k_retrieval: int = 15
    ):
        """
        Initialize RAG chain
        
        Args:
            vector_store: MovieVectorStore instance
            model_name: Ollama model name (llama3.2 or mistral)
            temperature: LLM temperature (0=deterministic, 1=creative)
            top_k_retrieval: Number of documents to retrieve
        """
        self.top_k = top_k_retrieval
        
        # Initialize or load vector store
        if vector_store is None:
            print("Loading vector store...")
            self.vector_store = MovieVectorStore()
            self.vector_store.collection = self.vector_store.client.get_collection(
                "netflix_gpt_movies"
            )
        else:
            self.vector_store = vector_store
        
        print(f"Vector store loaded: {self.vector_store.collection.count()} chunks available")
        
        # Initialize Ollama LLM
        print(f"Initializing LLM: {model_name}...")
        self.llm = Ollama(
            model=model_name,
            temperature=temperature,
            base_url="http://localhost:11434"  # Default Ollama URL
        )
        print("✅ LLM initialized")
        
        # Create prompt template
        self.prompt_template = self._create_prompt_template()
        
        # Create LLM chain
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template,
            verbose=False
        )
        
    def _create_prompt_template(self) -> PromptTemplate:
        """Create the prompt template for the LLM"""
        
        template = """You are Movie Recommender, an expert movie recommendation assistant. You help users discover movies based on their preferences.

You have access to a movie database with detailed information. Use the context below to provide accurate, helpful recommendations.

CONTEXT FROM MOVIE DATABASE:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
1. IF the user asks for movie recommendations:
   - CRITICAL FILTER COMPLIANCE: You will see a `[Filters: ...]` block in the User Question. You MUST strictly adhere to these criteria:
     * ONLY recommend movies matching the specified Genre (if not 'All').
     * ONLY recommend movies released within the specified Year range.
     * ONLY recommend movies with a quality score exceeding the Min Rating.
     * ONLY recommend the specified Content Type (Movies vs TV Shows).
     * If 'Streaming On' is specified (not 'All'), you MUST ONLY recommend movies currently available on that exact platform.
     * NEVER mention the `self-correction`, `[Filters: ...]`, or your filtering process in your response. Act naturally.
   - Return the exact number of movies requested by the user. If not specified, return 3.
   - Use this EXACT format for each movie:
     • Movie Title (Year) - One sentence why it matches.
2. IF the user asks for details about a specific movie:
   - Provide an engaging, descriptive paragraph about that movie.
   - At the very end of your response, on a new line, you MUST append the movie title and year in this EXACT format: "• Movie Title (Year) - "
   - Do NOT output a list of recommendations.
3. Keep the total response under 250 words.
4. No long descriptions or explanations. Be direct and concise.

RESPONSE:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def retrieve_context(
        self, 
        query: str, 
        filters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Retrieve relevant documents from vector store
        
        Args:
            query: User's search query
            filters: Optional metadata filters
            
        Returns:
            Dictionary with retrieved documents and metadata
        """
        print(f"🔍 Retrieving documents for: '{query}'")
        
        # Increase candidate pool wildly if filters require post-retrieval dropping
        # This prevents generic queries from returning 0 results due to top semantic matches missing the filter
        search_k = 500 if filters else self.top_k
        
        # Search vector store (pass None to avoid crashing ChromaDB on unsupported keys)
        results = self.vector_store.search(
            query=query,
            n_results=search_k,
            filter_metadata=None
        )
        
        # Format results
        retrieved_docs = []
        for doc, metadata, distance in zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ):
            # Exclude backend system collections from being passed to the RAG model or frontend
            if 'Collection' not in str(metadata.get('title', '')):
                retrieved_docs.append({
                    'content': doc,
                    'metadata': metadata,
                    'similarity_score': 1 - distance  # Convert distance to similarity
                })
        
        # Execute rigorous post-retrieval filtering in Python
        if filters:
            retrieved_docs = self._apply_post_retrieval_filters(retrieved_docs, filters)
            # Re-truncate to original requested size
            retrieved_docs = retrieved_docs[:self.top_k]
                
        print(f"✅ Retrieved {len(retrieved_docs)} relevant documents")
        
        return {
            'documents': retrieved_docs,
            'query': query
        }
        
    def _apply_post_retrieval_filters(self, docs: List[Dict], filters: Dict) -> List[Dict]:
        """Manually filter vector documents using exact metadata criteria and live TMDB streaming data concurrently."""
        import os
        import concurrent.futures
        import requests
        from dotenv import load_dotenv, find_dotenv
        
        load_dotenv(find_dotenv())
        TMDB_API_KEY = os.getenv("TMDB_API_KEY")
        
        req_provider = filters.get('provider', 'All')
        min_rating = filters.get('min_rating', 0.0)
        
        def _check_doc(doc):
            metadata = doc.get('metadata', {})
            
            # 1. Year Filter
            doc_year = metadata.get('year', 0)
            if filters.get('min_year') and doc_year < filters['min_year']:
                return None
            if filters.get('max_year') and doc_year > filters['max_year']:
                return None
                
            # 2. Genre Filter
            req_genre = filters.get('genre', 'All')
            if req_genre != 'All':
                doc_genres = metadata.get('genres', '')
                if isinstance(doc_genres, str):
                    if req_genre.lower() not in doc_genres.lower():
                        return None
                elif isinstance(doc_genres, list):
                    if not any(req_genre.lower() in g.lower() for g in doc_genres):
                        return None
            
            # 3. Content Type Filter
            req_type = filters.get('content_type', 'All')
            if req_type == 'TV Shows' and 'movie' in str(metadata.get('type', 'Movies')).lower():
                pass # Skipping enforcement since DB is exclusively movies
            
            # 4. TMDB Live Metadata Filter (Provider & Rating)
            if (req_provider != 'All' or min_rating > 0.0) and TMDB_API_KEY:
                title = metadata.get('title')
                if not title or title == 'Unknown':
                    return None
                try:
                    # Search TMDB for movie ID and rating
                    tmdb_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
                    res = requests.get(tmdb_url, timeout=2).json()
                    results = res.get('results', [])
                    if not results:
                        return None
                    
                    # Enforce Rating
                    if min_rating > 0.0:
                        tmdb_rating = results[0].get('vote_average', 0.0)
                        if tmdb_rating < min_rating:
                            return None # Drop Document
                    
                    # Enforce Provider
                    if req_provider != 'All':
                        movie_id = results[0]['id']
                        prov_url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={TMDB_API_KEY}"
                        prov_data = requests.get(prov_url, timeout=2).json()
                        flatrate = prov_data.get('results', {}).get('US', {}).get('flatrate', [])
                        
                        found_provider = False
                        for p in flatrate:
                            if req_provider.lower() in p.get('provider_name', '').lower() or \
                               ('apple' in req_provider.lower() and 'apple' in p.get('provider_name', '').lower()) or \
                               ('prime' in req_provider.lower() and 'prime' in p.get('provider_name', '').lower()):
                                found_provider = True
                                break
                                
                        if not found_provider:
                            return None # Drop Document
                except Exception:
                    return None # Drop Document if TMDB crashes during strict filtering
            
            return doc

        # Execute TMDB network requests for all candidate documents in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            verified_docs = list(executor.map(_check_doc, docs))
            
        # Strip failed payloads and cap limit natively
        filtered_docs = [d for d in verified_docs if d is not None]
        return filtered_docs[:self.top_k]
    
    def format_context(self, retrieved_docs: List[Dict]) -> str:
        """
        Format retrieved documents into context string for LLM
        
        Args:
            retrieved_docs: List of retrieved document dictionaries
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, doc in enumerate(retrieved_docs, 1):
            content = doc['content']
            metadata = doc['metadata']
            score = doc['similarity_score']
            
            title = metadata.get('title', 'Unknown')
            year = metadata.get('year', 'N/A')
            genres = metadata.get('genres', [])
            
            # Format genres
            if isinstance(genres, list):
                genres_str = ', '.join(genres)
            else:
                genres_str = str(genres)
            
            context_parts.append(
                f"[Document {i}] {title} ({year})\n"
                f"Genres: {genres_str}\n"
                f"Relevance: {score:.2f}\n"
                f"{content}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    def generate_response(
        self, 
        query: str,
        context: str
    ) -> str:
        """
        Generate LLM response using retrieved context
        
        Args:
            query: User's question
            context: Formatted context from retrieved documents
            
        Returns:
            LLM generated response
        """
        print("🤖 Generating response...")
        
        # Run the chain
        response = self.chain.run(
            question=query,
            context=context
        )
        
        return response.strip()
    
    def query(
        self, 
        question: str,
        filters: Optional[Dict] = None,
        return_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Main RAG query method
        
        Args:
            question: User's question/query
            filters: Optional metadata filters
            return_sources: Include source documents in response
            
        Returns:
            Dictionary with answer and optional sources
        """
        print("\n" + "="*70)
        print(f"📝 Query: {question}")
        print("="*70)
        
        # Step 1: Retrieve relevant documents
        retrieval_results = self.retrieve_context(question, filters)
        retrieved_docs = retrieval_results['documents']
        
        if not retrieved_docs:
            return {
                'question': question,
                'answer': "I couldn't find any relevant movies in the database. Could you try rephrasing your question?",
                'sources': [],
                'timestamp': datetime.now().isoformat()
            }
        
        # Step 2: Format context
        context = self.format_context(retrieved_docs)
        
        # Step 3: Generate response
        answer = self.generate_response(question, context)
        
        # Prepare response
        response = {
            'question': question,
            'answer': answer,
            'timestamp': datetime.now().isoformat()
        }
        
        import re
        if return_sources:
            # Extract explicitly generated movies from the response text
            mentioned_movies = []
            seen_titles = set()
            for line in answer.split('\n'):
                match = re.search(r'(.*?)\((\d{4})\)', line)
                if match:
                    raw_title = match.group(1)
                    year = match.group(2)
                    clean_title = re.sub(r'^[\s\d\.\-\*•]+', '', raw_title.replace('**', '').replace('*', '')).strip()
                    if clean_title and clean_title.lower() not in seen_titles:
                        mentioned_movies.append((clean_title, year))
                        seen_titles.add(clean_title.lower())
            
            doc_lookup = {
                str(doc['metadata'].get('title', '')).lower(): doc
                for doc in retrieved_docs
            }
            
            for (movie_title, movie_year) in mentioned_movies:
                clean_title = movie_title.strip()
                match = doc_lookup.get(clean_title.lower())
                if match:
                    sources.append({
                        'title': match['metadata'].get('title', clean_title),
                        'year': match['metadata'].get('year', movie_year),
                        'genres': match['metadata'].get('genres', []),
                        'similarity_score': match['similarity_score']
                    })
                else:
                    sources.append({
                        'title': clean_title,
                        'year': movie_year,
                        'genres': [],
                        'similarity_score': 0.99
                    })
            
            if not sources:
                # Limit fallback UI cards
                fallback_limit = 3
                for doc in retrieved_docs[:fallback_limit]:
                    sources.append({
                        'title': doc['metadata'].get('title', 'Unknown'),
                        'year': doc['metadata'].get('year', 'N/A'),
                        'genres': doc['metadata'].get('genres', []),
                        'similarity_score': doc['similarity_score']
                    })
            response['sources'] = sources
        
        print("\n✅ Response generated")
        print("="*70 + "\n")
        
        return response
    
    def batch_query(self, questions: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple queries
        
        Args:
            questions: List of questions
            
        Returns:
            List of response dictionaries
        """
        responses = []
        for question in questions:
            response = self.query(question)
            responses.append(response)
        return responses

class NetflixGPTWithMemory(NetflixGPTRAG):
    """
    RAG system with conversation memory
    Extends NetflixGPTRAG to add memory capabilities
    """
    
    def __init__(
        self,
        vector_store: MovieVectorStore = None,
        model_name: str = "llama3.2",
        temperature: float = 0.4,
        top_k_retrieval: int = 15,
        max_memory_turns: int = 5,
        session_id: str = None
    ):
        """
        Initialize RAG with memory
        
        Args:
            session_id: Optional session identifier for saving/loading
        """
        # Initialize parent RAG system
        super().__init__(vector_store, model_name, temperature, top_k_retrieval)
        
        # Initialize conversation memory
        self.memory = ConversationMemory(
            max_turns=max_memory_turns,
            persist_path=f"data/conversations/session_{session_id}.json" if session_id else None
        )
        
        print(f"✅ Conversation memory initialized (max {max_memory_turns} turns)")
        
        # Update prompt template to include conversation history
        self.prompt_template = self._create_memory_aware_prompt_template()
        
        # Recreate chain with new template
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template,
            verbose=False
        )
    
    def _create_memory_aware_prompt_template(self) -> PromptTemplate:
        """Create prompt template that includes conversation history"""
        
        template = """You are Movie Recommender, an expert movie recommendation assistant.

CONVERSATION HISTORY:
{conversation_history}

MOVIE DATABASE CONTEXT:
{context}

CURRENT USER QUESTION: {question}

Instructions:
Start with enthusiasm and a greeting.
1. Use conversation history to understand the request.
2. IF the user asks for movie recommendations:
   - CRITICAL FILTER COMPLIANCE: You will see a `[Filters: ...]` block in the User Question. You MUST strictly adhere to these criteria:
     * ONLY recommend movies matching the specified Genre (if not 'All').
     * ONLY recommend movies released within the specified Year range.
     * ONLY recommend movies with a quality score exceeding the Min Rating.
     * ONLY recommend the specified Content Type (Movies vs TV Shows).
     * If 'Streaming On' is specified (not 'All'), you MUST ONLY recommend movies currently available on that exact platform.
     * NEVER mention the `[Filters: ...]` block or your filtering process in your response. Act naturally as if you simply know these preferences.
   - Do not recommend movies already mentioned unless asked.
   - Respect user preferences.
   - Return the EXACT number of movies requested by the user. If not specified, return 3.
   - Format STRICTLY as a vertical list, one movie per item.
3. IF the user asks for details about a specific movie:
   - Provide an engaging, descriptive paragraph about that movie.
   - At the very end of your response, on a new line, you MUST append the movie title and year in this EXACT format: "• Movie Title (Year) - "
   - Do NOT output a list of recommendations.
4. Keep the entire response **under 250 words**.

USER PREFERENCES DETECTED:
{preferences}

RESPONSE:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["conversation_history", "context", "question", "preferences"]
        )
    
    def query_with_memory(
        self,
        question: str,
        filters: Optional[Dict] = None,
        return_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Query with conversation memory
        
        Args:
            question: User's question
            filters: Optional metadata filters
            return_sources: Include source documents
            
        Returns:
            Response dictionary with memory context
        """
        print("\n" + "="*70)
        print(f"📝 Query: {question}")
        
        # Check if it's a follow-up question
        is_followup = self.memory.is_follow_up_question(question)
        if is_followup:
            print("🔗 Detected as follow-up question")
            # Enhance query with context
            enhanced_question = self.memory.enhance_query_with_context(question)
            print(f"   Enhanced: {enhanced_question}")
        else:
            enhanced_question = question
        
        print("="*70)
        
        # Get recently mentioned movies to potentially filter out
        recent_movies = self.memory.get_recent_movies(n=10)
        
        # Step 1: Retrieve relevant documents
        retrieval_results = self.retrieve_context(enhanced_question, filters)
        retrieved_docs = retrieval_results['documents']
        
        if not retrieved_docs:
            response = {
                'question': question,
                'answer': "I couldn't find relevant movies. Could you try rephrasing?",
                'sources': [],
                'is_followup': is_followup,
                'conversation_turns': self.memory.turn_count,
                'timestamp': datetime.now().isoformat()
            }
            return response
        
        # Step 2: Format context
        context = self.format_context(retrieved_docs)
        
        # Step 3: Get conversation history
        conversation_history = self.memory.get_context_string(include_sources=False)
        if not conversation_history:
            conversation_history = "No previous conversation."
        
        # Step 4: Get preferences
        preferences = self.memory.get_preference_summary()
        
        # Step 5: Generate response with memory context
        print("🤖 Generating response with conversation context...")
        
        response_text = self.chain.run(
            conversation_history=conversation_history,
            context=context,
            question=question,
            preferences=preferences
        ).strip()
        
        # Prepare response
        response = {
            'question': question,
            'answer': response_text,
            'is_followup': is_followup,
            'conversation_turns': self.memory.turn_count,
            'timestamp': datetime.now().isoformat()
        }
        
        import re
        if return_sources:
            sources = []
            
            # Extract explicitly generated movies from the response text
            # Robust line-by-line parser targeting the year anchor (YYYY)
            mentioned_movies = []
            seen_titles = set()
            for line in response_text.split('\n'):
                match = re.search(r'(.*?)\((\d{4})\)', line)
                if match:
                    raw_title = match.group(1)
                    year = match.group(2)
                    clean_title = re.sub(r'^[\s\d\.\-\*•]+', '', raw_title.replace('**', '').replace('*', '')).strip()
                    if clean_title and clean_title.lower() not in seen_titles:
                        mentioned_movies.append((clean_title, year))
                        seen_titles.add(clean_title.lower())
            
            # Use retrieved docs metadata for baseline reference
            # map by title lowering
            doc_lookup = {
                str(doc['metadata'].get('title', '')).lower(): doc
                for doc in retrieved_docs
            }
            
            for (movie_title, movie_year) in mentioned_movies:
                # Get similarity score from baseline doc, if it exists
                clean_title = movie_title.strip()
                match = doc_lookup.get(clean_title.lower())
                
                if match:
                    sources.append({
                        'title': match['metadata'].get('title', clean_title),
                        'year': match['metadata'].get('year', movie_year),
                        'genres': match['metadata'].get('genres', []),
                        'similarity_score': match['similarity_score']
                    })
                else:
                    sources.append({
                        'title': clean_title,
                        'year': movie_year,
                        'genres': [],
                        'similarity_score': 0.99  # LLM synthesized it directly
                    })
            
            # If regex extraction fails or LLM formats badly, fallback to the original retrieve
            if not sources and retrieved_docs:
                # If conversational follow-up, only show the single most relevant movie card
                limit = 1 if is_followup else len(retrieved_docs)
                for doc in retrieved_docs[:limit]:
                    sources.append({
                        'title': doc['metadata'].get('title', 'Unknown'),
                        'year': doc['metadata'].get('year', 'N/A'),
                        'genres': doc['metadata'].get('genres', []),
                        'similarity_score': doc.get('similarity_score', 0.99)
                    })
            
            # Enrich sources with TMDB metadata for Next.js Frontend concurrently
            import os
            import time
            import concurrent.futures
            from dotenv import load_dotenv, find_dotenv
            
            load_dotenv(find_dotenv())
            TMDB_API_KEY = os.getenv("TMDB_API_KEY") # Use valid key from .env file
            
            def enrich_single_source(source):
                if not TMDB_API_KEY:
                    return source
                title = source.get('title')
                if not title or title == 'Unknown':
                    return source
                
                try:
                    tmdb_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
                    tmdb_res = requests.get(tmdb_url, timeout=5).json()
                    if tmdb_res.get('results') and len(tmdb_res['results']) > 0:
                        top_hit = tmdb_res['results'][0]
                        if top_hit.get('poster_path'):
                            source['poster_path'] = f"https://image.tmdb.org/t/p/w500{top_hit['poster_path']}"
                        source['overview'] = top_hit.get('overview', "A recommended movie.")
                        source['rating'] = round(top_hit.get('vote_average', 0.0), 1)
                        
                        movie_id = top_hit.get('id')
                        source['providers'] = []
                        source['cast'] = []
                        
                        if movie_id:
                            prov_url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={TMDB_API_KEY}"
                            try:
                                prov_res = requests.get(prov_url, timeout=5).json()
                                us_data = prov_res.get('results', {}).get('US', {})
                                flatrate = us_data.get('flatrate', [])
                                source['providers'] = [p['provider_name'] for p in flatrate]
                            except Exception:
                                pass
                                
                            cred_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_API_KEY}"
                            try:
                                cred_res = requests.get(cred_url, timeout=5).json()
                                cast_array = cred_res.get('cast', [])
                                source['cast'] = [actor['name'] for actor in cast_array[:5]]
                            except Exception:
                                pass
                except Exception as e:
                    import logging
                    logging.warning(f"Failed to fetch TMDB data for {title}: {e}")
                
                return source

            start_time = time.time()
            if sources:
                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    sources = list(executor.map(enrich_single_source, sources))
            end_time = time.time()
            print(f"⏱️ TMDB Parallel Enrichment completed in {end_time - start_time:.2f} seconds")
            
            response['sources'] = sources
        
        # Add to memory
        self.memory.add_turn(
            query=question,
            response=response_text,
            sources=response.get('sources', [])
        )
        
        print("\n✅ Response generated and added to memory")
        print("="*70 + "\n")
        
        return response
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get conversation memory summary"""
        return self.memory.get_summary()
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
        print("🗑️  Conversation memory cleared")
    
    def save_conversation(self, filepath: str = None):
        """Save conversation to file"""
        self.memory.save(filepath)
    
    def load_conversation(self, filepath: str):
        """Load conversation from file"""
        self.memory.load(filepath)


# Test function for memory-enabled RAG
def test_rag_with_memory():
    """Test RAG system with conversation memory"""
    
    print("\n" + "="*70)
    print("TESTING RAG WITH CONVERSATION MEMORY")
    print("="*70 + "\n")
    
    # Initialize
    rag = NetflixGPTWithMemory(
        model_name="llama3.2",
        temperature=0.7,
        max_memory_turns=5,
        session_id="test_session"
    )
    
    # Conversation sequence
    queries = [
        "I love action movies with great plots",
        "Tell me more about the first movie you mentioned",
        "What about something similar but more recent?",
        "Actually, I prefer comedies. What do you suggest?",
        "Those sound good, but I've already seen them"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*70}")
        print(f"TURN {i}/{len(queries)}")
        print(f"{'='*70}\n")
        
        response = rag.query_with_memory(query)
        
        print(f"❓ User: {response['question']}")
        print(f"🔗 Follow-up: {response['is_followup']}")
        print(f"💬 Turn: {response['conversation_turns']}")
        print(f"\n💡 Assistant:\n{response['answer']}\n")
        
        if response.get('sources'):
            print(f"📚 Sources:")
            for source in response['sources'][:3]:
                print(f"  • {source['title']} ({source['year']})")
        
        print("\n" + "-"*70)
        
        # Show memory summary
        if i == len(queries):
            print("\n📊 CONVERSATION SUMMARY:")
            summary = rag.get_memory_summary()
            for key, value in summary.items():
                print(f"  {key}: {value}")
    
    # Save conversation
    print("\n💾 Saving conversation...")
    rag.save_conversation()
    
    print("\n" + "="*70)
    print("✅ MEMORY TEST COMPLETE")
    print("="*70 + "\n")
    
    return rag

class NetflixGPTRobust(NetflixGPTWithMemory):
    """
    Production-ready RAG system with comprehensive error handling
    """
    
    def __init__(
        self,
        vector_store: MovieVectorStore = None,
        model_name: str = "llama3.2",
        temperature: float = 0.7,
        top_k_retrieval: int = 5,
        max_memory_turns: int = 5,
        session_id: str = None,
        enable_validation: bool = True
    ):
        """
        Initialize robust RAG system with error handling
        
        Args:
            enable_validation: Enable input validation and checks
        """
        self.enable_validation = enable_validation
        self.error_handler = ErrorHandler()
        self.input_validator = InputValidator()
        
        # Pre-flight checks
        if self.enable_validation:
            self._perform_startup_checks()
        
        # Initialize parent
        try:
            super().__init__(
                vector_store=vector_store,
                model_name=model_name,
                temperature=temperature,
                top_k_retrieval=top_k_retrieval,
                max_memory_turns=max_memory_turns,
                session_id=session_id
            )
        except Exception as e:
            raise OllamaConnectionError(f"Failed to initialize RAG system: {e}")
    
    def _perform_startup_checks(self):
        """Perform startup validation checks"""
        print("🔍 Performing startup checks...")
        
        # Check Ollama
        is_connected, error = self.error_handler.check_ollama_connection()
        if not is_connected:
            raise OllamaConnectionError(error)
        print("   ✅ Ollama connection OK")
    
    def _validate_before_query(self, query: str, filters: Optional[Dict] = None):
        """
        Validate inputs before processing query
        
        Args:
            query: User query
            filters: Optional filters
            
        Raises:
            QueryValidationError: If validation fails
        """
        if not self.enable_validation:
            return
        
        # Validate query
        is_valid, error = self.error_handler.validate_query(query)
        if not is_valid:
            raise QueryValidationError(error)
        
        # Validate filters
        if filters:
            is_valid, error = self.input_validator.validate_filters(filters)
            if not is_valid:
                raise QueryValidationError(error)
        
        # Validate vector store
        is_valid, error = self.error_handler.validate_vector_store(self.vector_store)
        if not is_valid:
            raise VectorStoreError(error)
    
    def query_safe(
        self,
        question: str,
        filters: Optional[Dict] = None,
        return_sources: bool = True,
        raise_on_error: bool = False
    ) -> Dict[str, Any]:
        """
        Safe query method with comprehensive error handling
        
        Args:
            question: User's question
            filters: Optional metadata filters
            return_sources: Include source documents
            raise_on_error: Raise exceptions instead of returning error response
            
        Returns:
            Response dictionary (includes 'error' key if failed)
        """
        try:
            # Sanitize input
            question = self.input_validator.sanitize_query(question)
            
            # Validate
            self._validate_before_query(question, filters)
            
            # Process query with memory
            response = self.query_with_memory(
                question=question,
                filters=filters,
                return_sources=return_sources
            )
            
            # Check if we got results
            if not response.get('sources') and return_sources:
                # No results found
                empty_response = self.error_handler.handle_empty_results(question)
                response['answer'] = empty_response['answer']
                response['error'] = 'no_results'
                response['suggestions'] = empty_response['suggestions']
            
            response['success'] = True
            return response
            
        except QueryValidationError as e:
            error_response = {
                'success': False,
                'error': 'validation_error',
                'error_message': str(e),
                'question': question,
                'answer': f"I couldn't process your question: {str(e)}"
            }
            if raise_on_error:
                raise
            return error_response
            
        except VectorStoreError as e:
            error_response = {
                'success': False,
                'error': 'vector_store_error',
                'error_message': str(e),
                'question': question,
                'answer': "There's an issue with the movie database. Please contact support."
            }
            if raise_on_error:
                raise
            return error_response
            
        except OllamaConnectionError as e:
            error_response = {
                'success': False,
                'error': 'llm_connection_error',
                'error_message': str(e),
                'question': question,
                'answer': (
                    "I'm having trouble connecting to the AI model. "
                    "Please make sure Ollama is running ('ollama serve')."
                )
            }
            if raise_on_error:
                raise
            return error_response
            
        except Exception as e:
            # Generic error handling
            error_response = {
                'success': False,
                'error': 'unknown_error',
                'error_message': str(e),
                'question': question,
                'answer': (
                    "I encountered an unexpected error. Please try rephrasing "
                    "your question or contact support if the issue persists."
                )
            }
            
            # Log the error
            print(f"\n❌ Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            if raise_on_error:
                raise
            return error_response
    
    @retry_on_failure(max_retries=2, delay=1.0, backoff=2.0)
    def query_with_retry(
        self,
        question: str,
        filters: Optional[Dict] = None,
        return_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Query with automatic retry on failure
        
        Args:
            question: User's question
            filters: Optional filters
            return_sources: Include sources
            
        Returns:
            Response dictionary
        """
        return self.query_safe(
            question=question,
            filters=filters,
            return_sources=return_sources,
            raise_on_error=True  # Raise to trigger retry
        )
    
    def batch_query_safe(
        self,
        questions: List[str],
        stop_on_error: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Process multiple queries safely
        
        Args:
            questions: List of questions
            stop_on_error: Stop processing on first error
            
        Returns:
            List of responses (includes errors)
        """
        responses = []
        
        for i, question in enumerate(questions, 1):
            print(f"\n📝 Processing query {i}/{len(questions)}...")
            
            response = self.query_safe(question, raise_on_error=False)
            responses.append(response)
            
            if not response['success'] and stop_on_error:
                print(f"⚠️  Stopping batch processing due to error")
                break
        
        return responses
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all components
        
        Returns:
            Health status dictionary
        """
        health = {
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # Check Ollama
        is_connected, error = self.error_handler.check_ollama_connection()
        health['checks']['ollama'] = {
            'status': 'ok' if is_connected else 'error',
            'message': error if error else 'Connected'
        }
        
        # Check Vector Store
        is_valid, error = self.error_handler.validate_vector_store(self.vector_store)
        health['checks']['vector_store'] = {
            'status': 'ok' if is_valid else 'error',
            'message': error if error else f"{self.vector_store.collection.count()} chunks available"
        }
        
        # Check Memory
        health['checks']['memory'] = {
            'status': 'ok',
            'message': f"{len(self.memory.history)} turns in memory"
        }
        
        # Overall status
        if any(check['status'] == 'error' for check in health['checks'].values()):
            health['overall_status'] = 'unhealthy'
        
        return health


# Test function with error scenarios
def test_error_scenarios():
    """Test various error scenarios"""
    
    print("\n" + "="*70)
    print("TESTING ERROR SCENARIOS")
    print("="*70 + "\n")
    
    try:
        # Initialize robust RAG
        print("Initializing robust RAG system...\n")
        rag = NetflixGPTRobust(
            model_name="llama3.2",
            enable_validation=True
        )
        
        # Test 1: Empty query
        print("1️⃣ Testing empty query:\n")
        response = rag.query_safe("")
        print(f"Success: {response['success']}")
        print(f"Error: {response.get('error')}")
        print(f"Message: {response['answer'][:100]}...\n")
        
        # Test 2: Too short query
        print("2️⃣ Testing too short query:\n")
        response = rag.query_safe("hi")
        print(f"Success: {response['success']}")
        print(f"Error: {response.get('error')}")
        print(f"Message: {response['answer'][:100]}...\n")
        
        # Test 3: Valid query
        print("3️⃣ Testing valid query:\n")
        response = rag.query_safe("Recommend action movies")
        print(f"Success: {response['success']}")
        if response['success']:
            print(f"Answer: {response['answer'][:150]}...")
            print(f"Sources: {len(response.get('sources', []))}")
        print()
        
        # Test 4: Query with invalid filter
        print("4️⃣ Testing invalid filter:\n")
        response = rag.query_safe(
            "Recommend movies",
            filters={'invalid_key': 'value'}
        )
        print(f"Success: {response['success']}")
        print(f"Error: {response.get('error')}")
        print()
        
        # Test 5: Batch query with errors
        print("5️⃣ Testing batch query:\n")
        queries = [
            "Good action movies",
            "",  # Invalid
            "Thriller recommendations",
        ]
        responses = rag.batch_query_safe(queries, stop_on_error=False)
        
        for i, resp in enumerate(responses, 1):
            print(f"Query {i}: {'✅ Success' if resp['success'] else '❌ Failed'}")
        print()
        
        # Test 6: Health check
        print("6️⃣ Performing health check:\n")
        health = rag.health_check()
        print(f"Overall Status: {health['overall_status']}")
        for component, status in health['checks'].items():
            icon = "✅" if status['status'] == 'ok' else "❌"
            print(f"{icon} {component}: {status['message']}")
        
        print("\n" + "="*70)
        print("✅ ERROR SCENARIO TESTS COMPLETE")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # test_rag_with_memory()  # Original test
    test_error_scenarios()  # New error tests

if __name__ == "__main__":
    # Run the original test
    # test_rag_system()
    
    # Run memory test
    test_rag_with_memory()

# Specialized query methods
class MovieQueryHelper:
    """Helper class for common movie query patterns"""
    
    @staticmethod
    def format_recommendation_query(mood: str = None, genre: str = None, era: str = None) -> str:
        """Generate a formatted query for recommendations"""
        parts = ["Recommend movies"]
        
        if mood:
            parts.append(f"for a {mood} mood")
        if genre:
            parts.append(f"in the {genre} genre")
        if era:
            parts.append(f"from the {era}")
        
        return " ".join(parts)
    
    @staticmethod
    def format_comparison_query(movie1: str, movie2: str) -> str:
        """Generate a comparison query"""
        return f"Compare {movie1} and {movie2}. What are the similarities and differences?"
    
    @staticmethod
    def format_similar_query(movie: str) -> str:
        """Generate a 'similar to' query"""
        return f"What movies are similar to {movie}? Recommend alternatives."
    
    @staticmethod
    def format_mood_query(mood: str) -> str:
        """Generate a mood-based query"""
        return f"Suggest movies that are perfect for when I'm feeling {mood}"


# Main execution and testing
def test_rag_system():
    """Test the RAG system with sample queries"""
    
    print("\n" + "="*70)
    print("TESTING Movie Recommender RAG SYSTEM")
    print("="*70 + "\n")
    
    # Initialize RAG system
    print("Initializing RAG system...")
    rag = NetflixGPTRAG(
        model_name="llama3.2",  # Change to "mistral" if you prefer
        temperature=0.7,
        top_k_retrieval=5
    )
    
    # Test queries
    test_queries = [
        "Recommend an exciting action movie",
        "I want to watch something funny and light-hearted",
        "What are some good thriller movies?",
        "Suggest a movie for a cozy weekend",
    ]
    
    print("\n" + "🎬"*35 + "\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}/{len(test_queries)}")
        print(f"{'='*70}")
        
        # Get response
        response = rag.query(query)
        
        # Display results
        print(f"\n❓ QUESTION:\n{response['question']}\n")
        print(f"💡 ANSWER:\n{response['answer']}\n")
        
        if response.get('sources'):
            print(f"📚 SOURCES ({len(response['sources'])} documents):")
            for j, source in enumerate(response['sources'], 1):
                print(f"  {j}. {source['title']} ({source['year']}) - Similarity: {source['similarity_score']:.2f}")
        
        print("\n" + "-"*70)
    
    print("\n" + "="*70)
    print("✅ RAG SYSTEM TEST COMPLETE")
    print("="*70 + "\n")
    
    return rag


if __name__ == "__main__":
    rag_system = test_rag_system()
