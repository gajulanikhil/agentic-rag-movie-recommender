import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from pathlib import Path
import json
from typing import List, Dict, Any
import re

class MovieVectorStore:
    """
    Manages ChromaDB vector store for movie documents
    """
    
    def __init__(
        self, 
        persist_directory: str = "data/vectorstore",
        collection_name: str = "netflix_gpt_movies",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the vector store
        
        Args:
            persist_directory: Where to save ChromaDB data
            collection_name: Name of the collection
            embedding_model: Sentence transformer model name
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Load embedding model
        print(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        print("✅ Embedding model loaded")
        
        # Get or create collection
        self.collection = None
        
    def create_collection(self, reset: bool = False):
        """Create or get ChromaDB collection"""
        if reset:
            try:
                self.client.delete_collection(name=self.collection_name)
                print(f"🗑️  Deleted existing collection: {self.collection_name}")
            except:
                pass
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Netflix GPT movie recommendation system"}
        )
        print(f"✅ Collection ready: {self.collection_name}")
        
    def chunk_text(self, text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Input text to chunk
            chunk_size: Target size in characters
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        # Split by sentences (simple approach)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            if current_size + sentence_size > chunk_size and current_chunk:
                # Save current chunk
                chunks.append(' '.join(current_chunk))
                
                # Start new chunk with overlap
                # Keep last few sentences for overlap
                overlap_sentences = []
                overlap_size = 0
                for s in reversed(current_chunk):
                    if overlap_size + len(s) <= overlap:
                        overlap_sentences.insert(0, s)
                        overlap_size += len(s)
                    else:
                        break
                
                current_chunk = overlap_sentences
                current_size = overlap_size
            
            current_chunk.append(sentence)
            current_size += sentence_size
        
        # Add final chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def prepare_documents(self, documents: List[Dict]) -> tuple:
        """
        Prepare documents for indexing
        
        Args:
            documents: List of document dicts with 'content' and 'metadata'
            
        Returns:
            Tuple of (texts, metadatas, ids)
        """
        all_texts = []
        all_metadatas = []
        all_ids = []
        
        for doc_idx, doc in enumerate(documents):
            content = doc['content']
            metadata = doc['metadata']
            
            # Chunk the document
            chunks = self.chunk_text(content)
            
            for chunk_idx, chunk in enumerate(chunks):
                # Create unique ID
                doc_id = f"doc_{doc_idx}_{chunk_idx}"
                
                # Add chunk metadata
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_index'] = chunk_idx
                chunk_metadata['total_chunks'] = len(chunks)
                chunk_metadata['doc_index'] = doc_idx
                
                all_texts.append(chunk)
                all_metadatas.append(chunk_metadata)
                all_ids.append(doc_id)
        
        return all_texts, all_metadatas, all_ids
    
    def add_documents(self, documents: List[Dict], batch_size: int = 100):
        """
        Add documents to the vector store
        
        Args:
            documents: List of documents to add
            batch_size: Number of documents to process at once
        """
        if self.collection is None:
            raise ValueError("Collection not initialized. Call create_collection() first.")
        
        print(f"\n📝 Preparing {len(documents)} documents for indexing...")
        texts, metadatas, ids = self.prepare_documents(documents)
        
        print(f"📊 Total chunks created: {len(texts)}")
        print(f"🔢 Processing in batches of {batch_size}...")
        
        # Add to ChromaDB in batches
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_metadatas = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(
                batch_texts, 
                show_progress_bar=False
            ).tolist()
            
            # Add to collection
            self.collection.add(
                documents=batch_texts,
                metadatas=batch_metadatas,
                ids=batch_ids,
                embeddings=embeddings
            )
            
            current_batch = (i // batch_size) + 1
            print(f"  ✓ Batch {current_batch}/{total_batches} indexed")
        
        print(f"\n✅ Successfully indexed {len(texts)} chunks from {len(documents)} documents")
        
    def search(
        self, 
        query: str, 
        n_results: int = 5,
        filter_metadata: Dict = None
    ) -> Dict[str, Any]:
        """
        Search the vector store
        
        Args:
            query: Search query text
            n_results: Number of results to return
            filter_metadata: Optional metadata filters (e.g., {'genre': 'Action'})
            
        Returns:
            Dictionary with results
        """
        if self.collection is None:
            raise ValueError("Collection not initialized.")
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Build where clause for filtering
        where_clause = filter_metadata if filter_metadata else None
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where=where_clause
        )
        
        return results
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        if self.collection is None:
            return {"error": "Collection not initialized"}
        
        count = self.collection.count()
        
        return {
            "collection_name": self.collection_name,
            "total_chunks": count,
            "persist_directory": str(self.persist_directory),
            "embedding_model": self.embedding_model_name
        }
    
    def test_retrieval(self, test_queries: List[str] = None):
        """
        Test the vector store with sample queries
        
        Args:
            test_queries: List of test queries (uses defaults if None)
        """
        if test_queries is None:
            test_queries = [
                "action movies with high ratings",
                "romantic comedies",
                "sci-fi thriller",
                "movies about time travel",
                "drama films from the 90s"
            ]
        
        print("\n🧪 Testing Vector Store Retrieval\n" + "="*60)
        
        for query in test_queries:
            print(f"\n📍 Query: '{query}'")
            results = self.search(query, n_results=3)
            
            if results['documents'][0]:
                print(f"   Found {len(results['documents'][0])} results:")
                for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                    title = metadata.get('title', 'Unknown')
                    print(f"   {i+1}. {title}")
                    print(f"      Preview: {doc[:100]}...")
            else:
                print("   ❌ No results found")
        
        print("\n" + "="*60)


# Utility function to load documents
def load_documents_from_json(json_path: str = "data/processed/movie_documents.json") -> List[Dict]:
    """Load documents from JSON file"""
    with open(json_path, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    return documents


# Main execution function
def main():
    """Main function to set up vector store"""
    print("="*60)
    print("NETFLIX GPT - Vector Store Setup")
    print("="*60)
    
    # Load documents
    print("\n1️⃣ Loading documents...")
    documents = load_documents_from_json()
    print(f"✅ Loaded {len(documents)} documents")
    
    # Initialize vector store
    print("\n2️⃣ Initializing vector store...")
    vector_store = MovieVectorStore(
        persist_directory="data/vectorstore",
        collection_name="netflix_gpt_movies",
        embedding_model="all-MiniLM-L6-v2"
    )
    
    # Create collection (reset=True to start fresh)
    print("\n3️⃣ Creating collection...")
    vector_store.create_collection(reset=True)
    
    # Add documents
    print("\n4️⃣ Indexing documents...")
    vector_store.add_documents(documents)
    
    # Get stats
    print("\n5️⃣ Collection Statistics:")
    stats = vector_store.get_collection_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test retrieval
    print("\n6️⃣ Testing retrieval...")
    vector_store.test_retrieval()
    
    print("\n" + "="*60)
    print("✅ Vector Store Setup Complete!")
    print("="*60)
    
    return vector_store


if __name__ == "__main__":
    vector_store = main()