"""
RAG Chain for Netflix GPT
Combines retrieval + LLM generation for movie recommendations
"""

from typing import List, Dict, Any, Optional
import json
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
        top_k_retrieval: int = 5
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
        
        template = """You are Netflix GPT, an expert movie recommendation assistant. You help users discover movies based on their preferences.

You have access to a movie database with detailed information. Use the context below to provide accurate, helpful recommendations.

CONTEXT FROM MOVIE DATABASE:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
1. Provide specific movie recommendations based on the context
2. Include movie titles, release years, and brief descriptions
3. Explain WHY each movie matches the user's request
4. If the context doesn't have perfect matches, recommend the closest alternatives
5. Be conversational and enthusiastic about movies
6. Always mention which movies from the database you're referring to

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
        
        # Search vector store
        results = self.vector_store.search(
            query=query,
            n_results=self.top_k,
            filter_metadata=filters
        )
        
        # Format results
        retrieved_docs = []
        for doc, metadata, distance in zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ):
            retrieved_docs.append({
                'content': doc,
                'metadata': metadata,
                'similarity_score': 1 - distance  # Convert distance to similarity
            })
        
        print(f"✅ Retrieved {len(retrieved_docs)} relevant documents")
        
        return {
            'documents': retrieved_docs,
            'query': query
        }
    
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
        
        if return_sources:
            # Add source information
            sources = []
            for doc in retrieved_docs:
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
        temperature: float = 0.7,
        top_k_retrieval: int = 5,
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
        
        template = """You are Netflix GPT, an expert movie recommendation assistant with memory of the conversation.

CONVERSATION HISTORY:
{conversation_history}

MOVIE DATABASE CONTEXT:
{context}

CURRENT USER QUESTION: {question}

INSTRUCTIONS:
1. Use the conversation history to understand context and follow-up questions
2. Avoid recommending movies already discussed (unless specifically requested)
3. Consider user preferences mentioned earlier in the conversation
4. Provide specific recommendations with titles, years, and descriptions
5. Explain WHY each movie matches the request
6. Be conversational and reference previous parts of the discussion naturally
7. If the user asks about "that movie" or "it", refer to the conversation history

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
        
        if return_sources:
            sources = []
            for doc in retrieved_docs:
                sources.append({
                    'title': doc['metadata'].get('title', 'Unknown'),
                    'year': doc['metadata'].get('year', 'N/A'),
                    'genres': doc['metadata'].get('genres', []),
                    'similarity_score': doc['similarity_score']
                })
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
    print("TESTING NETFLIX GPT RAG SYSTEM")
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