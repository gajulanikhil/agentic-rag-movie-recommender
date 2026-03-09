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

def inject_custom_css(theme="dark"):
    """Inject custom CSS for WhatsApp-style UI"""
    if theme == "dark":
        bg_gradient = "linear-gradient(to bottom, #0B141A 0%, #111B21 100%)"
        sidebar_bg = "#111b21"
        hero_color = "#25D366"
        text_main = "#E9EDEF"
        text_muted = "#8696A0"
        card_bg = "#202c33"
        btn_bg = "linear-gradient(135deg, #00A884 0%, #008F6F 100%)"
        btn_hover = "linear-gradient(135deg, #00BFA5 0%, #009688 100%)"
        chat_bg = "#0b141a"
        user_msg = "#005c4b"
        user_text = "#e9edef"
        bot_msg = "#202c33"
        bot_text = "#e9edef"
        border_color = "rgba(255,255,255,0.1)"
    else:
        bg_gradient = "linear-gradient(to bottom, #efeae2 0%, #f0f2f5 100%)"
        sidebar_bg = "#ffffff"
        hero_color = "#128C7E"
        text_main = "#111B21"
        text_muted = "#667781"
        card_bg = "#ffffff"
        btn_bg = "linear-gradient(135deg, #25D366 0%, #128C7E 100%)"
        btn_hover = "linear-gradient(135deg, #128C7E 0%, #075E54 100%)"
        chat_bg = "#efeae2"
        user_msg = "#d9fdd3"
        user_text = "#111b21"
        bot_msg = "#ffffff"
        bot_text = "#111b21"
        border_color = "rgba(0,0,0,0.1)"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    * {{
        font-family: 'Roboto', sans-serif;
    }}
    
    .stApp {{
        background: {bg_gradient};
    }}
    
    #MainMenu, footer, header {{visibility: hidden;}}
    
    .hero-title {{
        font-size: 3.5rem;
        color: {hero_color};
        text-align: center;
        font-weight: bold;
        margin-bottom: 0;
        letter-spacing: 0.05em;
    }}
    
    .hero-tagline {{
        font-size: 1.2rem;
        color: {text_muted};
        text-align: center;
        margin-top: 0.5rem;
        margin-bottom: 2rem;
    }}
    
    .netflix-divider {{
        height: 2px;
        background: {border_color};
        margin: 2rem 0;
    }}
    
    section[data-testid="stSidebar"] {{
        background: {sidebar_bg} !important;
        border-right: 1px solid {border_color};
    }}
    
    .sidebar-title {{
        color: {hero_color};
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1.5rem;
    }}
    
    .filter-header {{
        color: {text_main} !important;
        font-size: 1rem;
        font-weight: 600;
        margin-top: 1rem;
        border-left: 3px solid {hero_color};
        padding-left: 0.5rem;
    }}
    
    section[data-testid="stSidebar"] label, .streamlit-expanderHeader, p, div {{
        color: {text_main} !important;
    }}
    
    .chat-container {{
        background: {chat_bg};
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid {border_color};
        max-height: 500px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }}
    
    .chat-container::-webkit-scrollbar {{
        width: 8px;
    }}
    .chat-container::-webkit-scrollbar-track {{
        background: transparent;
    }}
    .chat-container::-webkit-scrollbar-thumb {{
        background: rgba(134, 150, 160, 0.3);
        border-radius: 10px;
    }}
    
    .message-row-user {{ display: flex; justify-content: flex-end; width: 100%; }}
    .message-row-assistant {{ display: flex; justify-content: flex-start; width: 100%; }}
    
    .user-message {{
        background: {user_msg};
        color: {user_text} !important;
        padding: 0.5rem 0.75rem;
        border-radius: 12px;
        border-top-right-radius: 4px;
        max-width: 75%;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        position: relative;
    }}
    .user-message * {{ color: {user_text} !important; }}
    
    .assistant-message {{
        background: {bot_msg};
        color: {bot_text} !important;
        padding: 0.5rem 0.75rem;
        border-radius: 12px;
        border-top-left-radius: 4px;
        max-width: 75%;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        position: relative;
    }}
    .assistant-message * {{ color: {bot_text} !important; }}
    
    .user-message::before {{
        content: ""; position: absolute; top: 0; right: -8px; width: 15px; height: 15px;
        background: linear-gradient(135deg, {user_msg} 0%, {user_msg} 50%, transparent 50%, transparent);
    }}
    .assistant-message::before {{
        content: ""; position: absolute; top: 0; left: -8px; width: 15px; height: 15px;
        background: linear-gradient(225deg, {bot_msg} 0%, {bot_msg} 50%, transparent 50%, transparent);
    }}
    
    .message-content {{ display: inline-block; font-size: 0.95rem; line-height: 1.4; color: inherit; }}
    .message-time {{ font-size: 0.65rem; color: {text_muted} !important; float: right; margin-left: 10px; margin-top: 10px; margin-bottom: -5px; }}
    
    .example-query {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 25px;
        padding: 0.6rem 1.2rem;
        margin: 0.4rem;
        display: inline-block;
        color: {text_main};
        cursor: pointer;
    }}
    .example-query:hover {{ border-color: {hero_color}; }}
    
    .stTextInput > div > div > input {{
        background: {card_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 25px !important;
        color: {text_main} !important;
    }}
    .stTextInput > div > div > input:focus {{ border-color: {hero_color} !important; box-shadow: none !important; }}
    
    .stButton > button {{
        background: {btn_bg};
        color: white !important;
        border-radius: 25px;
        border: none;
        padding: 0.7rem 2rem;
        width: 100%;
        font-weight: 600;
    }}
    .stButton > button:hover {{ background: {btn_hover}; color: white !important; }}
    
    .movie-card {{
        background: {card_bg};
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid {hero_color};
    }}
    .movie-title {{ color: {text_main}; font-size: 1.2rem; font-weight: bold; margin-bottom: 0.5rem; }}
    .movie-info {{ color: {text_muted} !important; font-size: 0.9rem; margin: 0.3rem 0; }}
    .movie-genre {{
        background: rgba(37, 211, 102, 0.2);
        color: {hero_color} !important;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        margin-right: 0.3rem;
        display: inline-block;
        margin-top: 0.3rem;
    }}
    
    .stat-box {{
        background: {card_bg};
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid {border_color};
    }}
    .stat-number {{ font-size: 2.5rem; color: {hero_color}; font-weight: bold; }}
    .stat-label {{ font-size: 0.9rem; color: {text_muted} !important; }}
    .info-box {{ background: {card_bg}; border-left: 4px solid {hero_color}; border-radius: 8px; padding: 1rem; color: {text_muted} !important; }}
    </style>
    """, unsafe_allow_html=True)
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
    if 'theme' not in st.session_state:
        st.session_state.theme = "dark"


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
            html = ''
            # html += f'''
            # <div class="movie-card">
            #     <div class="movie-title">🎬 {title}</div>
            #     <div class="movie-info">📅 {year} • Relevance: {score:.0%}</div>
            #     {f'<div class="movie-info">⭐ {rating}/10</div>' if rating else ''}
            #     <div style="margin-top: 0.5rem;">{genre_tags}</div>
            # </div>
            # '''
    
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
        st.markdown('<div class="sidebar-title">⚙️ Settings</div>', unsafe_allow_html=True)
        # Theme toggle
        is_dark = st.toggle("🌙 Dark Mode", value=(st.session_state.theme == 'dark'))
        st.session_state.theme = 'dark' if is_dark else 'light'
        
        st.markdown('<div class="netflix-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">🎯 Advanced Filters</div>', unsafe_allow_html=True)
        
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
    
    # Initialize session state FIRST
    initialize_session_state()
    
    # Render sidebar and get filters
    filters = render_sidebar()
    
    # Inject CSS based on theme
    inject_custom_css(st.session_state.theme)
    
    # Hero Section
    st.markdown('<h1 class="hero-title">WhatsApp Movie GPT</h1>', unsafe_allow_html=True)
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
            
            from markdown_it import MarkdownIt
            md = MarkdownIt()
            
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f'''
                    <div class="message-row-user">
                        <div class="user-message">
                            <span class="message-content">{md.render(message['content'])}</span>
                            <span class="message-time">{message.get('timestamp', 'Now')}</span>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    # Assistant message with enhanced display
                    st.markdown(f'''
                    <div class="message-row-assistant">
                        <div class="assistant-message">
                            <span class="message-content">{md.render(message['content'])}</span>
                            <span class="message-time">{message.get('timestamp', 'Now')}</span>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Show sources with inline WhatsApp attachment style
                    if message.get('sources'):
                        sources_with_posters = get_multiple_posters(message['sources'])
                        
                        # Use pure HTML flexbox instead of Streamlit columns so it dynamically wraps 1..N posters
                        html_content = '<div style="margin-top: 10px; margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 15px;">'
                        
                        # Dynamically size width based on poster count to mimic an expanding wrap (min 120px max wide)
                        width_css = "flex: 1 1 120px; max-width: 160px; min-width: 120px;" if len(sources_with_posters) > 1 else "max-width: 250px;"
                        
                        for source in sources_with_posters:
                            if source.get('poster_url'):
                                html_content += f'<div style="{width_css} background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid rgba(0,0,0,0.05);"><img src="{source["poster_url"]}" style="width: 100%; height: auto; display: block; object-fit: cover; aspect-ratio: 2/3;"><div style="padding: 8px;"><div style="font-size: 0.85rem; font-weight: bold; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #000000;">{source["title"]}</div><div style="font-size: 0.75rem; color: #667781;">{source.get("year", "")}</div></div></div>'
                            else:
                                html_content += f'<div style="{width_css} background: #ffffff; border-radius: 8px; padding: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid rgba(0,0,0,0.05); aspect-ratio: 2/3; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;"><div style="font-size: 2rem; margin-bottom: 5px;">🎬</div><div style="font-size: 0.85rem; font-weight: bold; color: #000000;">{source["title"]}</div><div style="font-size: 0.75rem; color: #667781;">{source.get("year", "")}</div></div>'
                        
                        html_content += '</div>'
                        st.markdown(html_content, unsafe_allow_html=True)
            
            #st.markdown('</div>', unsafe_allow_html=True)
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
        timestamp = datetime.now().strftime("%I:%M %p")
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
        <p>Powered by Group 14 - The Peter Pan Posse</p>
        <p style="font-size: 0.8rem;">Nikhil Gajula • Radhey Mutha • Muneeb Ahmed</p>
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()