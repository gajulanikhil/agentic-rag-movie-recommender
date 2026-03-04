#app.py
"""
Netflix GPT - Premium Streamlit Interface
Production-ready UI with Netflix styling
"""
from src.tmdb_integration import get_multiple_posters, get_movie_poster
import streamlit as st
from streamlit_lottie import st_lottie
import requests
import json
from datetime import datetime
from pathlib import Path
import sys

# Add src to path
sys.path.append('src')

from rag_chain import NetflixGPTRobust
from error_handler import ErrorHandler

# Page config MUST be first Streamlit command
st.set_page_config(
    page_title="Netflix GPT",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - NETFLIX PREMIUM THEME
# ============================================================================

def inject_custom_css():
    """Inject custom CSS for Netflix-style UI"""
    st.markdown("""
    <style>
    /* Import Netflix font */
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto:wght@300;400;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Roboto', sans-serif;
    }
    
    /* Main background */
    .stApp {
        background: linear-gradient(to bottom, #0B0B0B 0%, #141414 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hero Section */
    .hero-title {
        font-family: 'Bebas Neue', cursive;
        font-size: 5rem;
        color: #E50914;
        text-align: center;
        letter-spacing: 0.1em;
        text-shadow: 0 0 20px rgba(229, 9, 20, 0.5),
                     0 0 40px rgba(229, 9, 20, 0.3);
        margin-bottom: 0;
        animation: glow 2s ease-in-out infinite alternate;
    }
    # After hero title
    lottie_url = "https://assets5.lottiefiles.com/packages/lf20_khzniaya.json"  # Movie animation
    lottie_json = load_lottie_url(lottie_url)

    if lottie_json:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st_lottie(lottie_json, height=200, key="hero_animation")
    @keyframes glow {
        from {
            text-shadow: 0 0 10px rgba(229, 9, 20, 0.4),
                         0 0 20px rgba(229, 9, 20, 0.3);
        }
        to {
            text-shadow: 0 0 20px rgba(229, 9, 20, 0.6),
                         0 0 40px rgba(229, 9, 20, 0.4),
                         0 0 60px rgba(229, 9, 20, 0.2);
        }
    }
    
    .hero-tagline {
        font-size: 1.3rem;
        color: #B3B3B3;
        text-align: center;
        margin-top: 0.5rem;
        margin-bottom: 2rem;
        text-shadow: 0 0 10px rgba(179, 179, 179, 0.3);
    }
    
    /* Divider */
    .netflix-divider {
        height: 2px;
        background: linear-gradient(to right, 
            transparent 0%, 
            #E50914 50%, 
            transparent 100%);
        margin: 2rem 0;
        box-shadow: 0 0 10px rgba(229, 9, 20, 0.5);
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1F1F1F 0%, #0B0B0B 100%);
        border-right: 1px solid #E50914;
        box-shadow: 5px 0 15px rgba(229, 9, 20, 0.2);
    }
    
    section[data-testid="stSidebar"] > div {
        padding: 2rem 1rem;
    }
    
    /* Sidebar Title */
    .sidebar-title {
        color: #E50914;
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1.5rem;
        text-shadow: 0 0 10px rgba(229, 9, 20, 0.5);
    }
    
    /* Filter Section Headers */
    .filter-header {
        color: #FFFFFF;
        font-size: 1rem;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        padding-left: 0.5rem;
        border-left: 3px solid #E50914;
    }
    
    /* Streamlit widgets in sidebar */
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stSlider label {
        color: #B3B3B3 !important;
        font-size: 0.9rem;
    }
    
    /* Chat Container */
    .chat-container {
        background: rgba(31, 31, 31, 0.6);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(229, 9, 20, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        max-height: 500px;
        overflow-y: auto;
    }
    
    /* Custom Scrollbar */
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: rgba(11, 11, 11, 0.5);
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: #E50914;
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: #B20710;
    }
    
    /* Chat Messages */
    .user-message {
        background: linear-gradient(135deg, #E50914 0%, #B20710 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 0.5rem 0;
        margin-left: 20%;
        box-shadow: 0 4px 15px rgba(229, 9, 20, 0.3);
        animation: slideInRight 0.3s ease-out;
    }
    
    .assistant-message {
        background: rgba(45, 45, 45, 0.8);
        color: #E5E5E5;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        border-left: 3px solid #E50914;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
        animation: slideInLeft 0.3s ease-out;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Message metadata */
    .message-time {
        font-size: 0.7rem;
        color: #808080;
        margin-top: 0.3rem;
    }
    
    /* Example Queries */
    .example-query {
        background: rgba(31, 31, 31, 0.8);
        border: 1px solid rgba(229, 9, 20, 0.3);
        border-radius: 25px;
        padding: 0.6rem 1.2rem;
        margin: 0.4rem;
        display: inline-block;
        color: #E5E5E5;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.9rem;
    }
    
    .example-query:hover {
        background: linear-gradient(135deg, #E50914 0%, #B20710 100%);
        border-color: #E50914;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(229, 9, 20, 0.4);
    }
    
    /* Input Section */
    .stTextInput > div > div > input {
        background: rgba(31, 31, 31, 0.9) !important;
        border: 2px solid rgba(229, 9, 20, 0.3) !important;
        border-radius: 25px !important;
        color: white !important;
        padding: 1rem 1.5rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #E50914 !important;
        box-shadow: 0 0 20px rgba(229, 9, 20, 0.4) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #E50914 0%, #B20710 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.7rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(229, 9, 20, 0.3);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(229, 9, 20, 0.5);
        background: linear-gradient(135deg, #F40612 0%, #C00813 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Movie Card */
    .movie-card {
        background: rgba(31, 31, 31, 0.8);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #E50914;
        transition: all 0.3s ease;
    }
    
    .movie-card:hover {
        background: rgba(45, 45, 45, 0.9);
        transform: translateX(5px);
        box-shadow: 0 5px 20px rgba(229, 9, 20, 0.2);
    }
    
    .movie-title {
        color: #FFFFFF;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .movie-info {
        color: #B3B3B3;
        font-size: 0.9rem;
        margin: 0.3rem 0;
    }
    
    .movie-genre {
        display: inline-block;
        background: rgba(229, 9, 20, 0.2);
        color: #E50914;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        margin-right: 0.3rem;
        margin-top: 0.3rem;
    }
    
    /* Loading Spinner */
    .stSpinner > div {
        border-top-color: #E50914 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(31, 31, 31, 0.8);
        border-radius: 10px;
        color: #E5E5E5 !important;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(45, 45, 45, 0.9);
        border-left: 4px solid #E50914;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: rgba(0, 230, 118, 0.1) !important;
        border-left: 4px solid #00E676 !important;
        color: #00E676 !important;
    }
    
    .stError {
        background: rgba(229, 9, 20, 0.1) !important;
        border-left: 4px solid #E50914 !important;
        color: #FF6B6B !important;
    }
    
    .stWarning {
        background: rgba(255, 193, 7, 0.1) !important;
        border-left: 4px solid #FFC107 !important;
        color: #FFD54F !important;
    }
    
    /* Info box */
    .info-box {
        background: rgba(31, 31, 31, 0.6);
        border-left: 4px solid #E50914;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #B3B3B3;
    }
    
    /* Stats boxes */
    .stat-box {
        background: linear-gradient(135deg, rgba(229, 9, 20, 0.1) 0%, rgba(31, 31, 31, 0.8) 100%);
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(229, 9, 20, 0.2);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    .stat-number {
        font-size: 2.5rem;
        color: #E50914;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(229, 9, 20, 0.5);
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #B3B3B3;
        margin-top: 0.5rem;
    }
    
    /* Fade in animation */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    # Add this inside the <style> tag in inject_custom_css()

    /* Poster hover effect */
    .movie-card img {
        transition: all 0.3s ease;
    }
    
    .movie-card:hover img {
        transform: scale(1.05);
        box-shadow: 0 8px 16px rgba(229, 9, 20, 0.4);
    }
    
    /* Loading skeleton for images */
    .poster-skeleton {
        width: 100px;
        height: 150px;
        background: linear-gradient(
            90deg,
            rgba(31, 31, 31, 0.8) 25%,
            rgba(45, 45, 45, 0.9) 50%,
            rgba(31, 31, 31, 0.8) 75%
        );
        background-size: 200% 100%;
        animation: loading 1.5s infinite;
        border-radius: 8px;
    }
    
    @keyframes loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }            
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_lottie_url(url: str):
    """Load Lottie animation from URL"""
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

def initialize_session_state():
    """Initialize session state variables"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    
    if 'system_initialized' not in st.session_state:
        st.session_state.system_initialized = False
    
    if 'total_queries' not in st.session_state:
        st.session_state.total_queries = 0
    
    if 'current_input' not in st.session_state:
        st.session_state.current_input = ""

def initialize_rag_system():
    """Initialize the RAG system"""
    if not st.session_state.system_initialized:
        try:
            with st.spinner("🎬 Initializing Netflix GPT..."):
                session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.session_state.rag_system = NetflixGPTRobust(
                    model_name="llama3.2",
                    temperature=0.7,
                    max_memory_turns=5,
                    session_id=f"streamlit_{session_id}",
                    enable_validation=True
                )
                
                # Health check
                health = st.session_state.rag_system.health_check()
                
                if health['overall_status'] == 'unhealthy':
                    st.error("⚠️ System health check failed. Please check the sidebar for details.")
                    st.session_state.system_initialized = False
                    return False
                
                st.session_state.system_initialized = True
                return True
                
        except Exception as e:
            st.error(f"❌ Failed to initialize: {str(e)}")
            st.info("Please ensure:\n- Ollama is running: `ollama serve`\n- Vector store is set up: `python src/vectorstore.py`")
            st.session_state.system_initialized = False
            return False
    
    return True
def safe_get_posters(sources):
    """Safely get posters with fallback"""
    try:
        return get_multiple_posters(sources)
    except Exception as e:
        print(f"TMDB Error: {e}")
        # Return sources without posters
        for source in sources:
            source['poster_url'] = None
            source['backdrop_url'] = None
        return sources
    
def format_sources(sources):
    """Format source movies as cards with posters"""
    if not sources:
        return ""
    
    # Get posters for all sources
    try:
        sources_with_posters = get_multiple_posters(sources[:5])
    except:
        sources_with_posters = sources[:5]
    
    html = '<div style="margin-top: 1rem;">'
    
    for source in sources_with_posters:
        title = source.get('title', 'Unknown')
        year = source.get('year', 'N/A')
        genres = source.get('genres', [])
        score = source.get('similarity_score', 0)
        poster_url = source.get('poster_url')
        rating = source.get('vote_average')
        
        # Format genres
        if isinstance(genres, list):
            genre_tags = ''.join([f'<span class="movie-genre">{g}</span>' for g in genres[:3]])
        else:
            genre_tags = f'<span class="movie-genre">{genres}</span>'
        
        # Build card with poster
        if poster_url:
            html += f'''
            <div class="movie-card" style="display: flex; gap: 1rem;">
                <div style="flex-shrink: 0;">
                    <img src="{poster_url}" 
                         style="width: 100px; height: 150px; object-fit: cover; border-radius: 8px; 
                                box-shadow: 0 4px 8px rgba(0,0,0,0.3);"
                         alt="{title} poster">
                </div>
                <div style="flex-grow: 1;">
                    <div class="movie-title">🎬 {title}</div>
                    <div class="movie-info">📅 {year} • Relevance: {score:.0%}</div>
                    {f'<div class="movie-info">⭐ {rating}/10</div>' if rating else ''}
                    <div style="margin-top: 0.5rem;">{genre_tags}</div>
                </div>
            </div>
            '''
        else:
            # Fallback without poster
            html += f'''
            <div class="movie-card">
                <div class="movie-title">🎬 {title}</div>
                <div class="movie-info">📅 {year} • Relevance: {score:.0%}</div>
                {f'<div class="movie-info">⭐ {rating}/10</div>' if rating else ''}
                <div style="margin-top: 0.5rem;">{genre_tags}</div>
            </div>
            '''
    
    html += '</div>'
    return html

def set_example_query(query):
    """Set example query to input"""
    st.session_state.current_input = query

# ============================================================================
# SIDEBAR - FILTERS
# ============================================================================

def render_sidebar():
    """Render the sidebar with filters"""
    with st.sidebar:
        st.markdown('<div class="sidebar-title">🎯 Advanced Filters</div>', unsafe_allow_html=True)
        st.markdown('<div class="netflix-divider"></div>', unsafe_allow_html=True)
        
        # Genre filter
        st.markdown('<div class="filter-header">Genre</div>', unsafe_allow_html=True)
        genres = st.multiselect(
            "Select genres",
            ["Action", "Comedy", "Drama", "Thriller", "Sci-Fi", "Romance", 
             "Horror", "Documentary", "Animation", "Crime", "Fantasy"],
            key="genre_filter",
            label_visibility="collapsed"
        )
        
        # Year filter
        st.markdown('<div class="filter-header">Release Year</div>', unsafe_allow_html=True)
        year_range = st.slider(
            "Year range",
            1950, 2024, (1990, 2024),
            key="year_filter",
            label_visibility="collapsed"
        )
        
        # Rating filter
        st.markdown('<div class="filter-header">Minimum Rating</div>', unsafe_allow_html=True)
        min_rating = st.slider(
            "Rating",
            0.0, 10.0, 6.0, 0.5,
            key="rating_filter",
            label_visibility="collapsed"
        )
        
        # Type filter
        st.markdown('<div class="filter-header">Content Type</div>', unsafe_allow_html=True)
        content_type = st.selectbox(
            "Type",
            ["All", "Movies", "TV Shows"],
            key="type_filter",
            label_visibility="collapsed"
        )
        
        # Reset button
        st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
        if st.button("🔄 Reset Filters", use_container_width=True):
            st.session_state.genre_filter = []
            st.session_state.year_filter = (1990, 2024)
            st.session_state.rating_filter = 6.0
            st.session_state.type_filter = "All"
            st.rerun()
        
        # System Status
        st.markdown('<div class="netflix-divider" style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">📊 System Status</div>', unsafe_allow_html=True)
        
        if st.session_state.system_initialized and st.session_state.rag_system:
            health = st.session_state.rag_system.health_check()
            
            status_emoji = "✅" if health['overall_status'] == 'healthy' else "⚠️"
            st.markdown(f"**Status:** {status_emoji} {health['overall_status'].title()}")
            
            with st.expander("View Details"):
                for component, status in health['checks'].items():
                    icon = "✅" if status['status'] == 'ok' else "❌"
                    st.markdown(f"{icon} **{component.replace('_', ' ').title()}**")
                    st.caption(status['message'])
        else:
            st.warning("System not initialized")
        
        # Stats
        st.markdown('<div class="netflix-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">📈 Session Stats</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'''
            <div class="stat-box">
                <div class="stat-number">{st.session_state.total_queries}</div>
                <div class="stat-label">Queries</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'''
            <div class="stat-box">
                <div class="stat-number">{len(st.session_state.chat_history)}</div>
                <div class="stat-label">Messages</div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Clear chat button
        st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.total_queries = 0
            if st.session_state.rag_system:
                st.session_state.rag_system.clear_memory()
            st.rerun()
        
        return {
            'genres': genres,
            'year_range': year_range,
            'min_rating': min_rating,
            'content_type': content_type
        }

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application"""
    
    # Inject CSS
    inject_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar and get filters
    filters = render_sidebar()
    
    # Hero Section
    st.markdown('<h1 class="hero-title">NETFLIX GPT</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-tagline">Your AI-powered movie discovery assistant 🎬</p>', unsafe_allow_html=True)
    st.markdown('<div class="netflix-divider"></div>', unsafe_allow_html=True)
    
    # Initialize RAG system
    if not st.session_state.system_initialized:
        if not initialize_rag_system():
            st.stop()
    
    # Example queries section
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.markdown("### 💡 Try these examples:")
    
    example_queries = [
        "Suggest psychological thrillers like Shutter Island",
        "Best romantic movies from 2015 to 2020",
        "Feel good comedy movies for weekend",
        "Top rated crime TV shows",
        "Movies similar to Inception"
    ]
    
    # Create clickable example buttons
    cols = st.columns(len(example_queries))
    for idx, (col, query) in enumerate(zip(cols, example_queries)):
        with col:
            if st.button(f"💬 {query[:30]}...", key=f"example_{idx}", use_container_width=True):
                set_example_query(query)
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="netflix-divider"></div>', unsafe_allow_html=True)
    
    # Chat container
    st.markdown("### 💬 Conversation")
    
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.chat_history:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f'''
                    <div class="user-message">
                        {message['content']}
                        <div class="message-time">{message.get('timestamp', '')}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                # else:
                #     st.markdown(f'''
                #     <div class="assistant-message">
                #         {message['content']}
                #         <div class="message-time">{message.get('timestamp', '')}</div>
                #     </div>
                #     ''', unsafe_allow_html=True)
                else:
                    # Assistant message with enhanced display
                    st.markdown(f'''
                    <div class="assistant-message">
                        {message['content']}
                        <div class="message-time">{message.get('timestamp', '')}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Show sources with posters
                    if message.get('sources'):
                        with st.expander("📚 View Movie Details", expanded=False):
                            sources_html = format_sources(message['sources'])
                            st.markdown(sources_html, unsafe_allow_html=True)
                            
                            # Optional: Show as grid
                            cols = st.columns(min(3, len(message['sources'])))
                            sources_with_posters = get_multiple_posters(message['sources'][:3])
                            
                            for idx, (col, source) in enumerate(zip(cols, sources_with_posters)):
                                with col:
                                    if source.get('poster_url'):
                                        st.image(
                                            source['poster_url'],
                                            caption=f"{source['title']} ({source.get('year', 'N/A')})",
                                            use_container_width=True
                                        )
                                        if source.get('vote_average'):
                                            st.markdown(f"⭐ **{source['vote_average']}/10**")
                    
                    # Show sources if available
                    if message.get('sources'):
                        with st.expander("📚 View Sources"):
                            st.markdown(format_sources(message['sources']), unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div class="info-box">
                <p>👋 Welcome to Netflix GPT! I'm here to help you discover amazing movies and shows.</p>
                <p>💡 Ask me anything about movies - recommendations, comparisons, or specific genres!</p>
            </div>
            ''', unsafe_allow_html=True)
    
    # Input section
    st.markdown('<div class="netflix-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Ask me anything about movies...",
            value=st.session_state.current_input,
            placeholder="E.g., Recommend action movies with great plots...",
            key="user_query_input",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("🚀 Send", use_container_width=True)
    
    # Process query
    if send_button and user_input:
        # Reset current input
        st.session_state.current_input = ""
        
        # Add user message
        timestamp = datetime.now().strftime("%H:%M")
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': timestamp
        })
        
        # Generate response
        with st.spinner("🎬 Finding perfect recommendations..."):
            try:
                # Build filter dict (simplified for now)
                query_filters = None
                # You can enhance this to use sidebar filters if needed
                
                response = st.session_state.rag_system.query_safe(
                    user_input,
                    filters=query_filters,
                    return_sources=True,
                    raise_on_error=False
                )
                
                # Add assistant response
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response['answer'],
                    'sources': response.get('sources', []),
                    'timestamp': timestamp,
                    'success': response.get('success', True)
                })
                
                st.session_state.total_queries += 1
                
                # Show success/error
                if not response.get('success', True):
                    st.error(f"⚠️ {response.get('error', 'Unknown error')}")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': f"I encountered an error: {str(e)}",
                    'timestamp': timestamp,
                    'success': False
                })
        
        st.rerun()
    
    # Footer
    st.markdown('<div class="netflix-divider" style="margin-top: 3rem;"></div>', unsafe_allow_html=True)
    st.markdown('''
    <div style="text-align: center; color: #808080; padding: 2rem 0;">
        <p>Built with Streamlit • Powered by Ollama & ChromaDB</p>
        <p style="font-size: 0.8rem;">Netflix GPT © 2024 • Educational Project</p>
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()