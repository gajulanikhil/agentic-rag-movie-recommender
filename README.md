# Netflix GPT - AI-Powered Movie Recommendation System

<div align="center">

![Netflix GPT Banner](https://img.shields.io/badge/Netflix-GPT-E50914?style=for-the-badge&logo=netflix&logoColor=white)

**An intelligent movie discovery assistant powered by RAG (Retrieval-Augmented Generation)**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30.0-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1.0-00D4AA?style=flat)](https://www.langchain.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4.22-orange?style=flat)](https://www.trychroma.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Llama_3.2-000000?style=flat)](https://ollama.ai/)

[Features](#features) • [Demo](#demo) • [Installation](#installation) • [Usage](#usage) • [Architecture](#architecture) • [Contributing](#contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Demo](#demo)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Dataset Information](#dataset-information)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Performance](#performance)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Contact](#contact)

---

## 🎯 Overview

**Netflix GPT** is an advanced movie recommendation system that combines the power of Large Language Models (LLMs) with semantic search capabilities to provide intelligent, context-aware movie suggestions. Unlike traditional recommendation systems that rely solely on user ratings or collaborative filtering, Netflix GPT understands natural language queries and maintains conversation context to deliver personalized recommendations.

### What Makes It Special?

- 🧠 **Context-Aware Conversations**: Remembers previous interactions and provides follow-up recommendations
- 🎯 **Natural Language Understanding**: Ask questions like "movies similar to Inception" or "feel-good comedies for weekend"
- 🚀 **Semantic Search**: Finds movies based on meaning, not just keywords
- 💬 **Multi-Turn Dialogues**: Engage in natural conversations about movies
- 🎨 **Beautiful UI**: Netflix-inspired dark theme with smooth animations
- 🔒 **100% Free & Open Source**: No paid APIs, runs entirely on your local machine

### Use Cases

- **Movie Discovery**: Find hidden gems based on mood, genre, or plot themes
- **Personalized Recommendations**: Get suggestions that match your specific preferences
- **Movie Research**: Ask detailed questions about movies, directors, or genres
- **Comparison**: Compare movies and get detailed explanations of similarities
- **Conversational Exploration**: Discover movies through natural dialogue

---

## ✨ Features

### Core Functionality

- ✅ **Intelligent Recommendations**: Context-aware movie suggestions using RAG architecture
- ✅ **Conversation Memory**: Maintains context across multiple turns (up to 5 conversation turns)
- ✅ **Semantic Search**: Vector-based retrieval using sentence transformers
- ✅ **Advanced Filtering**: Filter by genre, year, rating, and content type
- ✅ **Follow-Up Questions**: Natural follow-up handling ("Tell me more about that movie")
- ✅ **Preference Tracking**: Learns and remembers user preferences during conversation
- ✅ **Error Handling**: Robust error handling with graceful degradation
- ✅ **Multi-Query Processing**: Batch query processing for efficiency

### User Interface

- 🎨 **Netflix-Themed UI**: Premium dark theme with Netflix red accents
- 💬 **ChatGPT-Style Interface**: Familiar chat bubble design
- 🎯 **Example Queries**: One-click example prompts to get started
- 📊 **Real-Time Statistics**: Session stats and conversation metrics
- 🏥 **System Health Monitor**: Live system status dashboard
- 🎭 **Movie Cards**: Rich movie information with metadata display
- 📚 **Source Citations**: Shows which movies were used for recommendations

### Technical Features

- ⚡ **Fast Response Times**: Optimized retrieval and generation (3-10 seconds)
- 💾 **Persistent Storage**: Conversation history saved across sessions
- 🔄 **Automatic Retry**: Retry logic for failed operations
- 🎛️ **Configurable Parameters**: Adjustable temperature, retrieval count, etc.
- 🧪 **Comprehensive Testing**: Full test suite for all components
- 📝 **Detailed Logging**: Debug and error logging throughout the pipeline

---

## 🎬 Demo

### Screenshot Gallery

**Main Interface**
```
[Netflix GPT Hero Section with glowing title]
↓
[Example Query Buttons]
↓
[Chat Interface with User/Assistant Messages]
↓
[Movie Recommendation Cards with Details]
```

### Example Interactions

**Query 1: Basic Recommendation**
```
User: "Recommend thrilling action movies"

Netflix GPT: "I'd recommend The Dark Knight (2008) - a gripping action thriller 
with exceptional plot depth. Also check out Mad Max: Fury Road (2015) for 
non-stop adrenaline-pumping action with stunning visuals."

📚 Sources: The Dark Knight, Mad Max: Fury Road, John Wick
```

**Query 2: Follow-Up Question**
```
User: "Tell me more about the first one"

Netflix GPT: "The Dark Knight is Christopher Nolan's masterpiece, featuring 
Heath Ledger's iconic Joker performance. It's a psychological thriller that 
explores themes of chaos vs order, making it more than just an action film..."

📚 Sources: The Dark Knight
```

**Query 3: Mood-Based Search**
```
User: "I want something uplifting for a bad day"

Netflix GPT: "For mood-boosting entertainment, try The Pursuit of Happyness 
(2006) - an inspiring true story about perseverance. Or Amélie (2001) for 
whimsical charm that'll lift your spirits."

📚 Sources: The Pursuit of Happyness, Amélie, The Intouchables
```

---

## 🛠️ Technology Stack

### Core Technologies

#### **Ollama** (Local LLM Runtime)
- **What it is**: An open-source tool that lets you run Large Language Models locally on your machine
- **Why we use it**: Provides free, private, and fast access to powerful AI models without API costs
- **Model Used**: Llama 3.2 (2GB) - Meta's efficient language model
- **Alternative**: Mistral 7B (4GB) - Larger, more capable model
- **Learn More**: [ollama.ai](https://ollama.ai/)

#### **LangChain** (LLM Framework)
- **What it is**: A framework for developing applications powered by language models
- **Why we use it**: Simplifies building RAG pipelines with modular components
- **Version**: 0.1.0
- **Components Used**: 
  - LLM Chains for prompt management
  - Document loaders and text splitters
  - Memory management utilities
- **Learn More**: [langchain.com](https://www.langchain.com/)

#### **ChromaDB** (Vector Database)
- **What it is**: An open-source embedding database for AI applications
- **Why we use it**: Stores and retrieves movie embeddings for semantic search
- **Version**: 0.4.22
- **Features Used**:
  - Persistent storage
  - Metadata filtering
  - Similarity search with cosine distance
- **Storage**: Local disk at `data/vectorstore/`
- **Learn More**: [trychroma.com](https://www.trychroma.com/)

#### **Sentence Transformers** (Embeddings)
- **What it is**: Python library for state-of-the-art sentence and text embeddings
- **Why we use it**: Converts text into numerical vectors for semantic similarity
- **Model Used**: `all-MiniLM-L6-v2`
  - Size: ~80MB
  - Dimensions: 384
  - Speed: Very fast
  - Quality: Good for general purposes
- **Learn More**: [sbert.net](https://www.sbert.net/)

### Supporting Technologies

#### **Streamlit** (Web Framework)
- **What it is**: Python framework for building data applications with simple Python scripts
- **Why we use it**: Rapid UI development with minimal code
- **Version**: 1.30.0
- **Features Used**:
  - Session state for conversation memory
  - Custom CSS for Netflix theming
  - Real-time updates
- **Learn More**: [streamlit.io](https://streamlit.io/)

#### **Pandas** (Data Processing)
- **What it is**: Fast, powerful data analysis and manipulation library
- **Why we use it**: Processing and merging movie datasets
- **Version**: 2.1.4
- **Use Case**: Cleaning and combining Netflix & TMDB datasets
- **Learn More**: [pandas.pydata.org](https://pandas.pydata.org/)

### Development Stack

```python
# Core ML/AI
langchain==0.1.0              # LLM framework
langchain-community==0.0.13   # Community integrations
chromadb==0.4.22              # Vector database
sentence-transformers==2.3.1   # Embeddings

# Data Processing
pandas==2.1.4                 # Data manipulation
numpy==1.26.3                 # Numerical computing

# Web Framework
streamlit==1.30.0             # UI framework

# Utilities
python-dotenv==1.0.0          # Environment variables
requests==2.31.0              # HTTP requests
```

---

## 🏗️ Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                     │
│                      (Streamlit Web App)                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ Error Handler│  │ Input        │  │ Query        │           │
│  │ & Validation │  │ Sanitizer    │  │ Processor    │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RAG Pipeline Layer                         │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  1. Query Enhancement (Conversation Context)           │     │
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                             │
│                   ▼                                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  2. Vector Retrieval (ChromaDB)                        │     │
│  │     - Semantic Search                                  │     │
│  │     - Top-K Selection (k=5)                            │     │
│  │     - Metadata Filtering                               │     │
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                             │
│                   ▼                                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  3. Context Formatting                                 │     │
│  │     - Document Ranking                                 │     │
│  │     - Prompt Construction                              │     │
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                             │
│                   ▼                                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  4. LLM Generation (Ollama - Llama 3.2)                │     │
│  │     - Prompt Processing                                │     │
│  │     - Response Generation                              │     │
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                             │
│                   ▼                                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  5. Memory Update (Conversation History)               │     │
│  │     - Save Turn                                        │     │
│  │     - Extract Preferences                              │     │
│  │     - Track Mentioned Movies                           │     │
│  └────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Storage Layer                         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ ChromaDB     │  │ Conversation │  │ Movie        │           │
│  │ Vector Store │  │ History JSON │  │ Documents    │           │
│  │ (Embeddings) │  │ (Sessions)   │  │ (Processed)  │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │ 
└─────────────────────────────────────────────────────────────────┘
```

### RAG Pipeline Flow

```
User Query: "Recommend action movies similar to John Wick"
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Step 1: Query Enhancement                              │
│ - Check conversation memory                            │
│ - Detect if follow-up question                         │
│ - Add context from previous turns                      │
│ Output: Enhanced query with context                    │
└────────────────┬───────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│ Step 2: Embedding Generation                           │
│ - Convert query to 384-dim vector                      │
│ - Using: all-MiniLM-L6-v2 model                        │
│ Output: [0.23, -0.15, 0.67, ..., 0.45]                 │
└────────────────┬───────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│ Step 3: Vector Similarity Search                       │
│ - Search ChromaDB collection                           │
│ - Find top-5 most similar movie chunks                 │ 
│ - Apply filters (genre, year, rating)                  │
│ Output: 5 relevant document chunks with scores         │
└────────────────┬───────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│ Step 4: Context Assembly                               │
│ - Format retrieved documents                           │
│ - Add conversation history                             │
│ - Build complete prompt                                │
│ Output: Structured prompt for LLM                      │
└────────────────┬───────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│ Step 5: LLM Generation                                 │
│ - Send prompt to Ollama (Llama 3.2)                    │
│ - Generate natural language response                   │
│ - Temperature: 0.7 (balanced creativity)               │
│ Output: Human-like recommendation text                 │
└────────────────┬───────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│ Step 6: Post-Processing                                │
│ - Extract movie titles mentioned                       │
│ - Add source citations                                 │
│ - Update conversation memory                           │
│ - Save to session state                                │
│ Output: Final response with metadata                   │
└────────────────┬───────────────────────────────────────┘
                 │
                 ▼
        Display to User with:
        - Answer text
        - Source movie cards
        - Metadata (year, genre, rating)
```

### Data Flow

```
Raw Data → Processing → Embeddings → Storage → Retrieval → Generation
   │           │            │           │          │            │
   │           │            │           │          │            │
   ▼           ▼            ▼           ▼          ▼            ▼
Netflix    Cleaning    Sentence    ChromaDB   Semantic    Ollama LLM
Dataset    Merging    Transformer   Vector      Search    Generation
  +         +Filter    Encoding     Database   Top-K      Response
TMDB       Extract      Model      Persistent  Results    Assembly
Dataset    Features                 Storage
```

---

## 📋 Prerequisites

### System Requirements

**Minimum:**
- **OS**: Windows 10/11, macOS 10.15+, Ubuntu 20.04+
- **RAM**: 8GB
- **Storage**: 5GB free space
- **CPU**: Any modern processor (Intel i5 or equivalent)
- **Internet**: Required for initial setup and dataset downloads

**Recommended:**
- **RAM**: 16GB (for better performance)
- **Storage**: 10GB free space
- **CPU**: Multi-core processor (Intel i7/AMD Ryzen 5 or better)
- **GPU**: Not required (CPU-only operation)

### Software Requirements

1. **Python 3.9 or higher**
   - Check version: `python --version`
   - Download: [python.org](https://www.python.org/downloads/)

2. **Git** (for cloning repository)
   - Check version: `git --version`
   - Download: [git-scm.com](https://git-scm.com/)

3. **Ollama** (LLM runtime)
   - Download: [ollama.ai/download](https://ollama.ai/download)
   - Installation guide included in [Installation](#installation) section

### Knowledge Prerequisites

- Basic command-line usage
- Basic understanding of Python (for customization)
- No machine learning knowledge required!

---

## 🚀 Installation

### Quick Start (5 Steps)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/agentic-rag-movie-recommender.git
cd agentic-rag-movie-recommender

# 2. Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Ollama and download model
# Follow Ollama installation below

# 5. Setup datasets and run
# Follow detailed steps below
```

### Detailed Installation Guide

#### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/agentic-rag-movie-recommender.git
cd agentic-rag-movie-recommender

# Verify you're in the right directory
ls
# Should show: app.py, src/, data/, requirements.txt
```

#### Step 2: Python Environment Setup

**Create Virtual Environment:**

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# You should see (venv) in your terminal
```

**Install Dependencies:**

```bash
# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# This will install:
# - langchain (LLM framework)
# - chromadb (vector database)
# - sentence-transformers (embeddings)
# - streamlit (web UI)
# - pandas (data processing)
# - and other dependencies
```

#### Step 3: Install Ollama

**Download Ollama:**

Choose your operating system:

- **Windows**: [Download Installer](https://ollama.ai/download/windows)
- **macOS**: [Download DMG](https://ollama.ai/download/mac)
- **Linux**:
  ```bash
  curl -fsSL https://ollama.ai/install.sh | sh
  ```

**Install LLM Model:**

```bash
# Pull Llama 3.2 (Recommended - 2GB)
ollama pull llama3.2

# OR pull Mistral (Alternative - 4GB, more capable)
ollama pull mistral

# Verify installation
ollama list
# Should display: llama3.2 or mistral
```

**Start Ollama Server:**

```bash
# Start Ollama (keep this running in a separate terminal)
ollama serve

# You should see:
# Listening on 127.0.0.1:11434 (version X.X.X)
```

> **Important**: Keep Ollama running in a separate terminal while using the application!

#### Step 4: Download Datasets

**Create Data Directories:**

```bash
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/vectorstore
mkdir -p data/conversations
```

**Download Required Datasets:**

You need to manually download these datasets from Kaggle:

1. **Netflix Movies and TV Shows Dataset**
   - URL: https://www.kaggle.com/datasets/shivamb/netflix-shows
   - File: `netflix_titles.csv`
   - Save to: `data/raw/netflix_titles.csv`
   - Size: ~3MB
   - Contains: 8,800+ titles

2. **TMDB 5000 Movie Dataset**
   - URL: https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata
   - Files needed:
     - `tmdb_5000_movies.csv`
     - `tmdb_5000_credits.csv`
   - Save to: `data/raw/`
   - Size: ~5MB total
   - Contains: 5,000+ movies with metadata

**Verify Downloads:**

```bash
ls data/raw/

# Should show:
# netflix_titles.csv
# tmdb_5000_movies.csv
# tmdb_5000_credits.csv
```

#### Step 5: Process Data & Build Vector Store

**Run Data Processing:**

```bash
# Process and merge datasets
python src/data_ingestion.py
```

**Expected Output:**
```
Processing Netflix data...
Netflix movies processed: 6131
Processing TMDB data...
TMDB movies processed: 4803
Merging datasets...
Combined dataset size: 10934
Creating movie documents...
Total documents created: 17

✅ Data processing complete!
Documents ready: 17 (minimum 10 required)
```

**Build Vector Database:**

```bash
# Create ChromaDB vector store
python src/vectorstore.py
```

**Expected Output:**
```
============================================================
NETFLIX GPT - Vector Store Setup
============================================================

1️⃣ Loading documents...
✅ Loaded 17 documents

2️⃣ Initializing vector store...
Loading embedding model: all-MiniLM-L6-v2
✅ Embedding model loaded

3️⃣ Creating collection...
✅ Collection ready: netflix_gpt_movies

4️⃣ Indexing documents...
📝 Preparing 17 documents for indexing...
📊 Total chunks created: 45
✓ Batch 1/1 indexed

✅ Successfully indexed 45 chunks from 17 documents

5️⃣ Collection Statistics:
   collection_name: netflix_gpt_movies
   total_chunks: 45
   
✅ Vector Store Setup Complete!
```

#### Step 6: Verify Installation

**Run Verification Scripts:**

```bash
# Test 1: Vector Store
python src/verify_vectorstore.py

# Test 2: RAG Pipeline
python src/verify_rag.py

# Test 3: Memory System
python src/verify_memory.py

# Test 4: Error Handling
python src/verify_phase6.py
```

**All tests should show:**
```
✅ All checks passed!
```

---

## ⚙️ Configuration

### Environment Variables

Currently, the project uses ChromaDB and Ollama locally, so no API keys are required for basic functionality.

### Model Configuration

Edit `src/rag_chain.py` to customize:

```python
# LLM Settings
model_name = "llama3.2"        # or "mistral"
temperature = 0.7              # 0.0 = deterministic, 1.0 = creative
max_memory_turns = 5           # conversation history length

# Retrieval Settings
top_k_retrieval = 5            # number of documents to retrieve

# Embedding Model
embedding_model = "all-MiniLM-L6-v2"  # sentence transformer model
```

### ChromaDB Configuration

Located in `src/vectorstore.py`:

```python
# Chunking Strategy
chunk_size = 800               # characters per chunk
overlap = 100                  # character overlap between chunks

# Collection Settings
collection_name = "netflix_gpt_movies"
persist_directory = "data/vectorstore"
```

### Streamlit Configuration

Create `.streamlit/config.toml` for custom settings:

```toml
[server]
port = 8501
headless = true

[theme]
primaryColor = "#E50914"
backgroundColor = "#0B0B0B"
secondaryBackgroundColor = "#1F1F1F"
textColor = "#FFFFFF"

[browser]
gatherUsageStats = false
```

---

## 📖 Usage

### Starting the Application

**Step 1: Start Ollama Server**

```bash
# In Terminal 1
ollama serve
```

**Step 2: Launch Streamlit App**

```bash
# In Terminal 2 (with venv activated)
streamlit run app.py
```

**Step 3: Access the Application**

The app will automatically open in your browser at:
- Local URL: `http://localhost:8501`
- Network URL: `http://YOUR_IP:8501`

### Using the Interface

#### 1. **Example Queries**

Click any example button to get started:
- "Suggest psychological thrillers like Shutter Island"
- "Best romantic movies from 2015 to 2020"
- "Feel good comedy movies for weekend"
- "Top rated crime TV shows"
- "Movies similar to Inception"

#### 2. **Custom Queries**

Type any movie-related question:
```
- "Recommend action movies with great plots"
- "What are some mind-bending sci-fi films?"
- "Show me award-winning dramas from the 90s"
- "Movies about time travel"
- "Something uplifting for a bad day"
```

#### 3. **Follow-Up Questions**

Engage in natural conversation:
```
User: "Recommend thriller movies"
Assistant: [Lists movies]

User: "Tell me more about the first one"
Assistant: [Detailed info about first movie]

User: "What about something similar but newer?"
Assistant: [Recent similar movies]
```

#### 4. **Using Filters (Sidebar)**

Advanced filtering options:
- **Genre**: Multi-select (Action, Comedy, Drama, etc.)
- **Year Range**: Slider (1950-2024)
- **Minimum Rating**: 0.0-10.0
- **Content Type**: Movies, TV Shows, or All

#### 5. **System Commands**

- **Clear Chat**: Remove conversation history
- **View Stats**: See session statistics
- **Health Check**: Check system status
- **Save Conversation**: Export chat history

### Command-Line Usage

#### Interactive Chat (Terminal)

```bash
python src/chat_with_memory.py
```

Features:
- Terminal-based chat interface
- All RAG features available
- Commands: `memory`, `health`, `clear`, `save`, `quit`

#### Running Tests

```bash
# Test RAG system
python src/rag_chain.py

# Test with specific queries
python src/test_interactive.py --quick

# Test error handling
python src/test_error_handling.py
```

#### Batch Processing

Process multiple queries:

```python
from src.rag_chain import NetflixGPTRobust

rag = NetflixGPTRobust()

queries = [
    "Action movies",
    "Romantic comedies",
    "Sci-fi thrillers"
]

responses = rag.batch_query_safe(queries)

for response in responses:
    print(response['answer'])
```

### API Usage (Python)

```python
from src.rag_chain import NetflixGPTRobust

# Initialize system
rag = NetflixGPTRobust(
    model_name="llama3.2",
    temperature=0.7,
    max_memory_turns=5
)

# Single query
response = rag.query_safe("Recommend action movies")
print(response['answer'])
print(response['sources'])

# With filters
filters = {'genre': 'Action', 'year': 2020}
response = rag.query_safe(
    "Recent action movies", 
    filters=filters
)

# Health check
health = rag.health_check()
print(health['overall_status'])

# Clear memory
rag.clear_memory()

# Save conversation
rag.save_conversation("data/conversations/my_session.json")
```

---

## 📁 Project Structure

```
agentic-rag-movie-recommender/
│
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .gitignore                     # Git ignore rules
│
├── data/                          # Data directory
│   ├── raw/                       # Raw datasets
│   │   ├── netflix_titles.csv
│   │   ├── tmdb_5000_movies.csv
│   │   └── tmdb_5000_credits.csv
│   │
│   ├── processed/                 # Processed data
│   │   ├── combined_movies.csv
│   │   ├── movie_documents.json
│   │   └── markdown_docs/         # Individual movie documents
│   │
│   ├── vectorstore/               # ChromaDB storage
│   │   └── [ChromaDB files]
│   │
│   └── conversations/             # Saved conversations
│       └── session_*.json
│
├── src/                           # Source code
│   ├── data_ingestion.py         # Data processing pipeline
│   ├── vectorstore.py            # Vector database management
│   ├── rag_chain.py              # RAG pipeline implementation
│   ├── conversation_memory.py    # Conversation memory system
│   ├── error_handler.py          # Error handling utilities
│   ├── utils.py                  # Helper functions
│   │
│   ├── chat_with_memory.py       # Terminal chat interface
│   ├── test_interactive.py       # Interactive testing
│   ├── test_error_handling.py    # Error handling tests
│   │
│   ├── verify_vectorstore.py     # Vector store verification
│   ├── verify_rag.py             # RAG pipeline verification
│   ├── verify_memory.py          # Memory system verification
│   └── verify_phase6.py          # Error handling verification
│
├── notebooks/                     # Jupyter notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_test_vectorstore.ipynb
│   ├── 03_rag_examples.ipynb
│   └── 04_memory_examples.ipynb
│
└── docs/                          # Documentation
    └── ERROR_HANDLING.md          # Error handling guide
```

### Key Files Explained

#### **app.py**
Main Streamlit web application with Netflix-themed UI. Contains all frontend code and user interaction logic.

#### **src/rag_chain.py**
Core RAG pipeline implementation:
- `NetflixGPTRAG`: Basic RAG system
- `NetflixGPTWithMemory`: RAG + conversation memory
- `NetflixGPTRobust`: Production-ready with error handling

#### **src/vectorstore.py**
Vector database management:
- Document chunking and embedding
- ChromaDB collection management
- Semantic search implementation

#### **src/conversation_memory.py**
Conversation memory system:
- Turn-based history management
- Follow-up question detection
- User preference extraction

#### **src/error_handler.py**
Comprehensive error handling:
- Input validation
- Connection error handling
- Graceful degradation

#### **src/data_ingestion.py**
Data processing pipeline:
- Dataset loading and cleaning
- Movie document creation
- Metadata extraction

---

## 🔍 How It Works

### RAG (Retrieval-Augmented Generation) Explained

**Traditional LLMs:**
```
User Query → LLM → Response
```
**Problem**: LLM only knows what it was trained on (knowledge cutoff)

**RAG Approach:**
```
User Query → Retrieve Relevant Info → LLM + Retrieved Context → Response
```
**Benefit**: LLM can access current, specific information from your data

### Our Implementation

#### Phase 1: Document Preparation
```python
# 1. Load movie datasets (Netflix + TMDB)
movies = load_datasets()

# 2. Create rich text documents
documents = create_movie_documents(movies)
# Example document:
"""
# The Dark Knight (2008)
Genres: Action, Crime, Drama
Director: Christopher Nolan
Cast: Christian Bale, Heath Ledger

Overview:
When the menace known as the Joker wreaks havoc...
"""

# 3. Split into chunks (800 characters each)
chunks = split_documents(documents)

# 4. Convert to embeddings (vectors)
embeddings = encode_chunks(chunks)
# [0.23, -0.15, 0.67, ..., 0.45]  (384 dimensions)

# 5. Store in ChromaDB
store_in_database(chunks, embeddings)
```

#### Phase 2: Query Processing
```python
# User asks: "Recommend action movies"

# 1. Convert query to embedding
query_embedding = encode("Recommend action movies")

# 2. Find similar documents (cosine similarity)
similar_docs = chromadb.search(query_embedding, top_k=5)
# Returns: 5 most relevant movie chunks

# 3. Build prompt with context
prompt = f"""
Context from movie database:
{similar_docs}

User question: Recommend action movies

Provide recommendations based on the context above.
"""

# 4. Send to LLM (Ollama - Llama 3.2)
response = llm.generate(prompt)

# 5. Return formatted response with sources
return {
    'answer': response,
    'sources': [doc.metadata for doc in similar_docs]
}
```

#### Phase 3: Conversation Memory
```python
# Conversation flow:

Turn 1:
User: "Recommend thrillers"
System: Stores query + response
Memory: [Turn 1]

Turn 2:
User: "Tell me more about the first one"
System: Detects follow-up, retrieves Turn 1
Enhanced Query: "Tell me more about [Movie from Turn 1]"
Memory: [Turn 1, Turn 2]

Turn 3:
User: "Something similar but newer"
System: Uses context from Turn 1 & 2
Enhanced Query: "Movies similar to [Movie] but newer"
Memory: [Turn 1, Turn 2, Turn 3]
```

### Embeddings Explained Simply

**Text to Numbers:**
```
"The Dark Knight" → [0.23, -0.15, 0.67, ..., 0.45]
"Batman movie"    → [0.21, -0.14, 0.68, ..., 0.43]

Similar meanings → Similar vectors → Close in vector space
```

**Semantic Search:**
```
Query: "superhero films"
Matches:
- "The Dark Knight" (high similarity)
- "Iron Man" (high similarity)  
- "The Notebook" (low similarity) ❌
```

**Why it works:**
The model learned that "superhero" and "Batman" are related concepts through training on billions of text examples.

---

## 📊 Dataset Information

### Netflix Movies and TV Shows Dataset

**Source**: Kaggle  
**Link**: https://www.kaggle.com/datasets/shivamb/netflix-shows  
**License**: CC0: Public Domain  

**Statistics**:
- Total titles: 8,807
- Movies: 6,131
- TV Shows: 2,676
- Date range: 1925-2021
- Countries: 100+

**Columns Used**:
- `show_id`: Unique identifier
- `type`: Movie or TV Show
- `title`: Title of the content
- `director`: Director name
- `cast`: Main cast members
- `country`: Production country
- `date_added`: Date added to Netflix
- `release_year`: Original release year
- `rating`: Content rating (PG, R, etc.)
- `duration`: Runtime or seasons
- `listed_in`: Genres
- `description`: Plot summary

### TMDB 5000 Movie Dataset

**Source**: Kaggle  
**Link**: https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata  
**License**: CC0: Public Domain  

**Statistics**:
- Total movies: 4,803
- Date range: 1916-2017
- Average rating: 6.0/10
- Total cast members: 20,000+

**Columns Used**:
- `id`: TMDB ID
- `title`: Movie title
- `overview`: Plot description
- `genres`: Genre list (JSON)
- `release_date`: Release date
- `vote_average`: User rating (0-10)
- `vote_count`: Number of votes
- `runtime`: Duration in minutes
- `cast`: Cast information (JSON)
- `crew`: Crew information (JSON)

### Data Processing Pipeline

```
Raw Data (14,000+ entries)
    │
    ▼
Cleaning & Filtering
- Remove duplicates
- Filter incomplete records
- Standardize formats
    │
    ▼
Merging Datasets
- Combine Netflix + TMDB
- Enrich with metadata
- Remove conflicts
    │
    ▼
Document Creation
- Select top-rated movies
- Create genre collections
- Format as markdown
    │
    ▼
Final Dataset (17 documents, 45 chunks)
```

### Document Types Created

1. **Individual Movie Documents** (12 documents)
   - High-rated movies (score > 7.0)
   - Popular movies (votes > 1000)
   - Rich metadata included

2. **Genre Collection Documents** (5 documents)
   - Top genres: Action, Comedy, Drama, Thriller, Sci-Fi
   - Contains 10 movies per genre
   - Thematic summaries

**Example Document Structure:**
```markdown
# Inception (2010)

**Genres**: Sci-Fi, Thriller, Action
**Director**: Christopher Nolan
**Cast**: Leonardo DiCaprio, Joseph Gordon-Levitt, Ellen Page

## Overview
A thief who steals corporate secrets through the use of 
dream-sharing technology is given the inverse task of 
planting an idea into the mind of a C.E.O.

## Key Information
- Release Year: 2010
- Rating: 8.8/10
- Runtime: 148 minutes
- Type: Movie
```

---

## 🔧 API Documentation

### Core Classes

#### **NetflixGPTRobust**

Main RAG system with error handling.

```python
from src.rag_chain import NetflixGPTRobust

# Initialize
rag = NetflixGPTRobust(
    vector_store=None,           # Optional: pre-loaded vector store
    model_name="llama3.2",       # LLM model name
    temperature=0.7,              # 0.0-1.0 creativity
    top_k_retrieval=5,           # Number of docs to retrieve
    max_memory_turns=5,          # Conversation history length
    session_id="my_session",     # Optional: session identifier
    enable_validation=True       # Enable input validation
)
```

**Methods:**

```python
# Query with error handling
response = rag.query_safe(
    question="Recommend action movies",
    filters=None,                 # Optional: metadata filters
    return_sources=True,         # Include source documents
    raise_on_error=False         # Return error dict instead of raising
)

# Response format:
{
    'success': True,
    'question': "Recommend action movies",
    'answer': "I recommend The Dark Knight...",
    'sources': [
        {
            'title': 'The Dark Knight',
            'year': 2008,
            'genres': ['Action', 'Crime'],
            'similarity_score': 0.85
        }
    ],
    'is_followup': False,
    'conversation_turns': 1,
    'timestamp': '2024-01-15T10:30:00'
}

# Query with retry
response = rag.query_with_retry(
    question="...",
    filters=None,
    return_sources=True
)

# Batch processing
responses = rag.batch_query_safe(
    questions=[...],
    stop_on_error=False
)

# Health check
health = rag.health_check()
# Returns:
{
    'overall_status': 'healthy',  # or 'unhealthy'
    'checks': {
        'ollama': {'status': 'ok', 'message': 'Connected'},
        'vector_store': {'status': 'ok', 'message': '45 chunks available'},
        'memory': {'status': 'ok', 'message': '3 turns in memory'}
    }
}

# Memory operations
summary = rag.get_memory_summary()
rag.clear_memory()
rag.save_conversation("path/to/file.json")
rag.load_conversation("path/to/file.json")
```

#### **MovieVectorStore**

Vector database management.

```python
from src.vectorstore import MovieVectorStore

# Initialize
vector_store = MovieVectorStore(
    persist_directory="data/vectorstore",
    collection_name="netflix_gpt_movies",
    embedding_model="all-MiniLM-L6-v2"
)

# Create collection
vector_store.create_collection(reset=False)

# Add documents
documents = [...]  # List of document dicts
vector_store.add_documents(documents, batch_size=100)

# Search
results = vector_store.search(
    query="action movies",
    n_results=5,
    filter_metadata={'genre': 'Action'}  # Optional
)

# Get statistics
stats = vector_store.get_collection_stats()
```

#### **ConversationMemory**

Conversation history management.

```python
from src.conversation_memory import ConversationMemory

# Initialize
memory = ConversationMemory(
    max_turns=5,                 # Keep last 5 turns
    memory_type="buffer",        # "buffer" or "summary"
    persist_path="path/to/save.json"
)

# Add conversation turn
memory.add_turn(
    query="Recommend movies",
    response="I recommend...",
    sources=[...],
    metadata={}
)

# Get context
context = memory.get_context_string(include_sources=True)

# Check if follow-up
is_followup = memory.is_follow_up_question("Tell me more about that")

# Enhance query with context
enhanced_query = memory.enhance_query_with_context("What about that one?")

# Get preferences
preferences = memory.get_preference_summary()

# Get recent movies
recent_movies = memory.get_recent_movies(n=10)

# Save/Load
memory.save("path/to/file.json")
memory.load("path/to/file.json")

# Clear
memory.clear()
```

### Error Handling

#### **ErrorHandler**

```python
from src.error_handler import ErrorHandler

handler = ErrorHandler()

# Validate query
is_valid, error_msg = handler.validate_query("user query")

# Check Ollama connection
is_connected, error_msg = handler.check_ollama_connection()

# Validate vector store
is_valid, error_msg = handler.validate_vector_store(vector_store)

# Handle empty results
response = handler.handle_empty_results("query")
```

#### **Custom Exceptions**

```python
from src.error_handler import (
    NetflixGPTError,           # Base exception
    OllamaConnectionError,     # Ollama issues
    VectorStoreError,          # Vector store issues
    QueryValidationError,      # Invalid input
    NoResultsError             # No results found
)

try:
    response = rag.query_safe("...", raise_on_error=True)
except QueryValidationError as e:
    print(f"Invalid query: {e}")
except OllamaConnectionError as e:
    print(f"Ollama not available: {e}")
```

### Utilities

#### **Helper Functions**

```python
from src.utils import (
    save_conversation,
    load_conversation,
    format_conversation_history,
    extract_movie_titles,
    calculate_query_statistics
)

# Save conversation
save_conversation(
    conversation=[...],
    filename="my_session.json"
)

# Load conversation
conversation = load_conversation("my_session.json")

# Format for display
formatted = format_conversation_history(conversation)

# Extract movie titles
titles = extract_movie_titles(response)

# Calculate statistics
stats = calculate_query_statistics(responses)
```

---

## 🐛 Troubleshooting

### Common Issues and Solutions

#### **1. Ollama Connection Error**

**Symptom:**
```
❌ Cannot connect to Ollama. Please make sure Ollama is running.
```

**Solutions:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it:
ollama serve

# Verify model is downloaded:
ollama list

# If model missing:
ollama pull llama3.2
```

#### **2. Vector Store is Empty**

**Symptom:**
```
❌ Vector store has only 0 chunks (minimum 10 required)
```

**Solutions:**
```bash
# Re-run data processing
python src/data_ingestion.py
python src/vectorstore.py

# Verify
python src/verify_vectorstore.py
```

#### **3. Module Not Found Errors**

**Symptom:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**Solutions:**
```bash
# Ensure virtual environment is activated
# You should see (venv) in terminal

# Reinstall requirements
pip install -r requirements.txt

# If still issues, try:
pip install --upgrade pip
pip install --force-reinstall -r requirements.txt
```

#### **4. Datasets Not Found**

**Symptom:**
```
FileNotFoundError: data/raw/netflix_titles.csv not found
```

**Solutions:**
```bash
# Verify files exist
ls data/raw/

# Should show:
# - netflix_titles.csv
# - tmdb_5000_movies.csv
# - tmdb_5000_credits.csv

# If missing, download from Kaggle (see Installation section)
```

#### **5. Slow Response Times**

**Symptom:**
Queries take >30 seconds

**Solutions:**

1. **Use smaller model:**
   ```python
   # In src/rag_chain.py
   model_name = "llama3.2"  # Instead of "mistral"
   ```

2. **Reduce retrieval count:**
   ```python
   top_k_retrieval = 3  # Instead of 5
   ```

3. **Lower temperature:**
   ```python
   temperature = 0.3  # Faster, more focused
   ```

4. **Check system resources:**
   ```bash
   # Close other applications
   # Ensure adequate RAM available
   ```

#### **6. Port Already in Use**

**Symptom:**
```
OSError: [Errno 48] Address already in use
```

**Solutions:**
```bash
# Use different port
streamlit run app.py --server.port 8502

# Or kill existing process
# macOS/Linux:
lsof -ti:8501 | xargs kill -9

# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

#### **7. Memory Errors (RAM)**

**Symptom:**
```
MemoryError: Unable to allocate array
```

**Solutions:**

1. **Reduce batch size:**
   ```python
   # In src/vectorstore.py
   vector_store.add_documents(docs, batch_size=50)  # Instead of 100
   ```

2. **Use smaller embedding model:**
   ```python
   # Consider: "all-MiniLM-L6-v2" (current)
   # Even smaller: "paraphrase-MiniLM-L3-v2"
   ```

3. **Close other applications**

#### **8. Conversation Not Saving**

**Symptom:**
Conversation lost after refresh

**Solutions:**

1. **Click "Save" button before closing**

2. **Check save location:**
   ```bash
   ls data/conversations/
   # Should show session_*.json files
   ```

3. **Manual save:**
   ```python
   rag.save_conversation("data/conversations/my_session.json")
   ```

### Debug Mode

Enable debug logging:

```python
# Add to top of app.py or scripts
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting More Help

1. **Check logs** in terminal for error messages
2. **Run verification scripts** to identify issues
3. **Check GitHub Issues** for similar problems
4. **Create new issue** with error details

---

## ⚡ Performance

### Benchmarks

Tested on: MacBook Pro M1, 16GB RAM

| Operation | Time | Notes |
|-----------|------|-------|
| Initial Setup | 15-20 min | One-time |
| Data Processing | 2-3 min | One-time |
| Vector Store Build | 1-2 min | One-time |
| App Startup | 5-10 sec | Each time |
| First Query | 8-12 sec | Cold start |
| Subsequent Queries | 3-5 sec | Warm |
| Follow-up Questions | 2-4 sec | Context cached |

### Optimization Tips

**For Faster Responses:**

1. **Use Llama 3.2** (2GB) instead of Mistral (4GB)
2. **Lower temperature** to 0.3-0.5 for faster generation
3. **Reduce top_k_retrieval** to 3 instead of 5
4. **Keep Ollama running** to avoid cold starts
5. **Close unused applications** to free RAM

**For Better Quality:**

1. **Use Mistral** for more sophisticated responses
2. **Increase temperature** to 0.7-0.9 for creativity
3. **Increase top_k_retrieval** to 7-10 for more context
4. **Add more documents** to vector store

### Resource Usage

| Component | RAM Usage | Disk Usage |
|-----------|-----------|------------|
| Ollama (Llama 3.2) | ~2.5GB | 2GB |
| ChromaDB | ~200MB | 50MB |
| Streamlit | ~300MB | - |
| Python Dependencies | ~500MB | 500MB |
| **Total** | **~3.5GB** | **~3GB** |

---

## 🗺️ Roadmap

### Completed ✅
- [x] Basic RAG pipeline
- [x] Vector database with ChromaDB
- [x] Conversation memory (5 turns)
- [x] Error handling & validation
- [x] Streamlit web interface
- [x] Netflix-themed UI
- [x] Session management
- [x] Batch query processing
- [x] Health monitoring

### In Progress 🚧
- [ ] Advanced filtering by director/actor
- [ ] User authentication system
- [ ] Multi-language support
- [ ] Export recommendations to PDF

### Planned 🎯

**Short-term (Next 2-4 weeks)**
- [ ] Movie trailer integration (YouTube API)
- [ ] Watch provider information (JustWatch API)
- [ ] Collaborative filtering recommendations
- [ ] User rating system
- [ ] Bookmark/watchlist feature

**Medium-term (1-3 months)**
- [ ] Fine-tuned embedding model for movies
- [ ] Advanced query understanding (sentiment, mood)
- [ ] Multi-modal search (describe plot, upload images)
- [ ] Social features (share recommendations)
- [ ] Recommendation explanations (why this movie?)

**Long-term (3-6 months)**
- [ ] Mobile app (React Native)
- [ ] Real-time Netflix catalog updates
- [ ] Integration with streaming services
- [ ] Personalized user profiles
- [ ] A/B testing framework
- [ ] Analytics dashboard

### Feature Requests

Have an idea? [Open an issue](https://github.com/yourusername/agentic-rag-movie-recommender/issues) with the `enhancement` label!

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute

- 🐛 **Report Bugs**: Found an issue? [Open a bug report](https://github.com/yourusername/agentic-rag-movie-recommender/issues/new?template=bug_report.md)
- 💡 **Suggest Features**: Have ideas? [Request a feature](https://github.com/yourusername/agentic-rag-movie-recommender/issues/new?template=feature_request.md)
- 📝 **Improve Documentation**: Fix typos, add examples, clarify instructions
- 🎨 **Enhance UI**: Improve design, add animations, fix responsiveness
- 🔧 **Code Contributions**: Fix bugs, implement features, optimize performance

### Development Setup

```bash
# Fork the repository on GitHub

# Clone your fork
git clone https://github.com/YOUR_USERNAME/agentic-rag-movie-recommender.git
cd agentic-rag-movie-recommender

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/agentic-rag-movie-recommender.git

# Create a branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Add: your feature description"

# Push to your fork
git push origin feature/your-feature-name

# Open a Pull Request on GitHub
```

### Coding Standards

- **Python**: Follow PEP 8 style guide
- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Add type hints for function parameters
- **Comments**: Explain complex logic
- **Testing**: Add tests for new features

### Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass**: Run verification scripts
4. **Update CHANGELOG.md** with your changes
5. **Request review** from maintainers

### Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on collaboration
- Welcome newcomers

### Dataset Licenses

- **Netflix Dataset**: CC0 Public Domain
- **TMDB Dataset**: CC0 Public Domain

### Third-Party Licenses

This project uses open-source libraries. See their respective licenses:
- Streamlit: Apache 2.0
- LangChain: MIT
- ChromaDB: Apache 2.0
- Sentence Transformers: Apache 2.0

---

## 🙏 Acknowledgments

### Datasets
- **Netflix Shows Dataset** on Kaggle
- **TMDB 5000 Movie Dataset** on Kaggle

### Technologies
- **Ollama Team** - For making local LLMs accessible
- **LangChain Community** - For the excellent RAG framework
- **ChromaDB Team** - For the efficient vector database
- **Sentence Transformers** - For powerful embeddings
- **Streamlit Team** - For the amazing web framework

### Inspiration
- ChatGPT's conversational interface
- Netflix's user experience design
- Open-source AI community

### Special Thanks
- All contributors who helped improve this project
- Beta testers who provided valuable feedback
- Open-source community for resources and support

---

## 📧 Contact

### Maintainer
**Your Name**
- GitHub: [@gajulanikhil](https://github.com/gajulanikhil)
- Email: gajulanikhil39@gmail.com
- LinkedIn: [gajula-nikhil](https://www.linkedin.com/in/gajula-nikhil/)


### Support
- 📖 **Documentation**: Check this README and docs folder
- 💬 **Discussions**: Ask questions in GitHub Discussions
- 🐛 **Bug Reports**: Open an issue with details
- 💡 **Feature Requests**: Suggest in GitHub Issues

---

**Made with ❤️ by [Nikhil Gajula](https://github.com/gajulanikhil)**

**Powered by Open Source**

[⬆ Back to Top](#agentic-rag-movie-recommender---ai-powered-movie-recommendation-system)

</div>

---

## 🎓 Learning Resources

Want to learn more about the technologies used?

### RAG (Retrieval-Augmented Generation)
- [LangChain RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)
- [RAG Explained (Video)](https://www.youtube.com/watch?v=T-D1OfcDW1M)
- [Building RAG Applications](https://www.pinecone.io/learn/retrieval-augmented-generation/)

### Vector Databases
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Vector Embeddings Explained](https://www.pinecone.io/learn/vector-embeddings/)
- [Semantic Search Tutorial](https://www.sbert.net/examples/applications/semantic-search/README.html)

### LLMs & Ollama
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Llama 3.2 Model Card](https://huggingface.co/meta-llama/Llama-3.2-3B)
- [Running LLMs Locally](https://www.youtube.com/watch?v=Wjrdr0NU4Sk)

### Streamlit
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Gallery](https://streamlit.io/gallery)
- [Custom Components](https://docs.streamlit.io/develop/concepts/custom-components)

---

**Last Updated**: March 2025  
**Version**: 1.0.0  
**Status**: Active Development