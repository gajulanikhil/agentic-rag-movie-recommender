import re

def update_app():
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    css_replacement = '''def inject_custom_css(theme="dark"):
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
'''

    # Replace CSS function
    start = content.find("def inject_custom_css():")
    end = content.find('def load_lottie_url(url: str):')
    
    if start != -1 and end != -1:
        content = content[:start] + css_replacement + content[end:]
        
    # Add theme state mapping
    state_mapping = """    if 'theme' not in st.session_state:
        st.session_state.theme = "dark"
"""
    if "'theme' not in st.session_state:" not in content:
        content = content.replace("    if 'current_input' not in st.session_state:\n        st.session_state.current_input = \"\"",
                                  "    if 'current_input' not in st.session_state:\n        st.session_state.current_input = \"\"\n" + state_mapping)

    # Change render_sidebar
    sidebar_old = """    with st.sidebar:
        st.markdown('<div class="sidebar-title">🎯 Advanced Filters</div>', unsafe_allow_html=True)
        st.markdown('<div class="netflix-divider"></div>', unsafe_allow_html=True)"""
    
    sidebar_new = """    with st.sidebar:
        st.markdown('<div class="sidebar-title">⚙️ Settings</div>', unsafe_allow_html=True)
        # Theme toggle
        is_dark = st.toggle("🌙 Dark Mode", value=(st.session_state.theme == 'dark'))
        st.session_state.theme = 'dark' if is_dark else 'light'
        
        st.markdown('<div class="netflix-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">🎯 Advanced Filters</div>', unsafe_allow_html=True)"""
        
    content = content.replace(sidebar_old, sidebar_new)

    # Change main() ordering & hero text
    main_old = """    # Inject CSS
    inject_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar and get filters
    filters = render_sidebar()"""
    
    main_new = """    # Initialize session state FIRST
    initialize_session_state()
    
    # Render sidebar and get filters
    filters = render_sidebar()
    
    # Inject CSS based on theme
    inject_custom_css(st.session_state.theme)"""
    
    content = content.replace(main_old, main_new)
    
    hero_old = """'<h1 class="hero-title">NETFLIX GPT</h1>'"""
    hero_new = """'<h1 class="hero-title">WhatsApp Movie GPT</h1>'"""
    content = content.replace(hero_old, hero_new)

    # Note: replacing with exact match for hero-title
    content = content.replace('<h1 class="hero-title">NETFLIX GPT</h1>', '<h1 class="hero-title">WhatsApp Movie GPT</h1>')

    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_app()
