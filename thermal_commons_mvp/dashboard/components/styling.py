"""Modern CSS and styling for COOL dashboard."""

import streamlit as st


def inject_custom_css() -> None:
    """Inject modern CSS styling into Streamlit."""
    css = """
    <style>
    /* Night Galaxy color scheme - deep dark with cosmic accents */
    :root {
        --primary: #8B5CF6;
        --secondary: #A78BFA;
        --accent: #EC4899;
        --success: #10B981;
        --bg-dark: #000000;
        --bg-card: #0F0F1E;
        --bg-gradient-start: #000000;
        --bg-gradient-end: #0A0A1A;
        --text-primary: #E5E7EB;
        --text-secondary: #9CA3AF;
        --galaxy-purple: #4C1D95;
        --galaxy-blue: #1E1B4B;
        --star-gold: #FBBF24;
    }
    
    /* Main container - no excess padding/skeleton boxes */
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        max-width: 1400px;
    }
    
    /* Title styling - Galaxy theme */
    h1 {
        background: linear-gradient(135deg, #8B5CF6 0%, #EC4899 50%, #A78BFA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.02em;
        text-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
    }
    
    /* Subheaders */
    h2, h3 {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Metrics - Galaxy glow style */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: var(--primary) !important;
        text-shadow: 0 0 10px rgba(139, 92, 246, 0.5);
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }
    
    /* Cards and containers - Dark galaxy */
    .stMetric {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.4) 0%, rgba(76, 29, 149, 0.3) 100%);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        padding: 1rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.1);
    }
    
    /* Selectboxes and inputs - Dark galaxy */
    .stSelectbox > div > div {
        background-color: var(--bg-card) !important;
        border: 1px solid rgba(139, 92, 246, 0.4) !important;
        border-radius: 8px !important;
        box-shadow: 0 0 10px rgba(139, 92, 246, 0.1);
    }
    
    /* Expanders - Dark galaxy */
    .streamlit-expanderHeader {
        background: rgba(15, 15, 30, 0.8) !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        font-weight: 600 !important;
        border: 1px solid rgba(139, 92, 246, 0.2) !important;
    }
    
    /* Dataframes - Dark galaxy */
    .dataframe {
        background: rgba(15, 15, 30, 0.9) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(139, 92, 246, 0.2) !important;
    }
    
    /* Captions */
    .stCaption {
        color: var(--text-secondary) !important;
        font-size: 0.85rem !important;
    }
    
    /* Info boxes - Dark galaxy */
    .stInfo {
        background: rgba(30, 27, 75, 0.3) !important;
        border-left: 4px solid var(--primary) !important;
        border-radius: 8px !important;
        box-shadow: 0 0 10px rgba(139, 92, 246, 0.2);
    }
    
    /* Success/Warning/Error */
    .stSuccess {
        background: rgba(6, 255, 165, 0.1) !important;
        border-left: 4px solid var(--success) !important;
        border-radius: 8px !important;
    }
    
    .stWarning {
        background: rgba(255, 193, 7, 0.1) !important;
        border-left: 4px solid #FFC107 !important;
        border-radius: 8px !important;
    }
    
    .stError {
        background: rgba(255, 0, 110, 0.1) !important;
        border-left: 4px solid var(--accent) !important;
        border-radius: 8px !important;
    }
    
    /* Sidebar (if used) */
    [data-testid="stSidebar"] {
        background: var(--bg-dark) !important;
    }
    
    /* Charts container */
    [data-testid="stChart"] {
        background: var(--bg-card) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    /* Night Galaxy gradient background */
    .stApp {
        background: linear-gradient(180deg, #000000 0%, #0A0A1A 50%, #1E1B4B 100%);
        background-attachment: fixed;
    }
    
    /* Main container - darker */
    .main {
        background: transparent !important;
    }
    
    /* Main content container background */
    .main .block-container {
        background: transparent !important;
    }
    
    /* Remove visible outlines / fill for top-level padding boxes while keeping inner cards */
    .main .block-container > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Remove empty layout / skeleton boxes completely - no padding, no space */
    section[data-testid="stVerticalBlock"]:empty,
    div[data-testid="stVerticalBlock"]:empty,
    [data-testid="column"]:empty,
    div[data-testid="stHorizontalBlock"]:empty {
        display: none !important;
        padding: 0 !important;
        margin: 0 !important;
        min-height: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-dark);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--secondary);
    }
    
    /* Button styling - Galaxy glow */
    button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%) !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 15px rgba(139, 92, 246, 0.4) !important;
    }
    
    button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.6) !important;
    }
    
    /* Strip skeleton/empty wrappers - no padding, no visible box */
    .element-container,
    div[data-testid="stElementContainer"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Also ensure bare markdown wrappers never appear as empty cards/skeletons */
    .stMarkdown,
    div[data-testid="stMarkdown"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Table styling */
    table {
        background: var(--bg-card) !important;
        border-radius: 8px !important;
    }
    
    th {
        background: rgba(0, 212, 255, 0.2) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }
    
    td {
        color: var(--text-secondary) !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 5px rgba(0, 212, 255, 0.5); }
        50% { box-shadow: 0 0 20px rgba(0, 212, 255, 0.8); }
    }
    
    /* Section dividers */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.5), transparent);
        margin: 2rem 0;
    }
    
    /* Enhanced selectbox styling */
    .stSelectbox label {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    /* Chart titles - Galaxy theme */
    h3 {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.5) 0%, rgba(76, 29, 149, 0.4) 100%);
        padding: 0.75rem 1rem;
        border-radius: 8px;
        border-left: 4px solid var(--primary);
        margin-bottom: 1rem !important;
        box-shadow: 0 0 15px rgba(139, 92, 246, 0.2);
    }
    
    /* Better spacing */
    .stMarkdown {
        margin-bottom: 1rem;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--success);
        margin-right: 0.5rem;
        animation: pulse 2s infinite;
    }
    
    /* Better table styling */
    .dataframe {
        border-collapse: separate;
        border-spacing: 0;
    }
    
    .dataframe thead th {
        position: sticky;
        top: 0;
        z-index: 10;
    }
    
    /* Selectbox dropdown */
    .stSelectbox [data-baseweb="select"] {
        background-color: var(--bg-card) !important;
    }
    
    /* Compact metrics - reduce padding */
    [data-testid="stMetric"] {
        padding: 0.5rem !important;
    }
    
    /* No extra spacing from skeleton/wrapper boxes */
    .element-container {
        margin-bottom: 0 !important;
    }
    
    /* Compact selectbox */
    .stSelectbox {
        margin-bottom: 0.5rem !important;
    }
    
    /* Minimal gap between real sections; empty skeleton blocks are hidden via CSS/JS */
    section[data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }
    
    /* Custom scrollbar for dataframes */
    .dataframe-container {
        max-height: 400px;
        overflow-y: auto;
    }
    
    /* Trade log table - prevent page stretching */
    [data-testid="stDataFrame"] {
        max-height: 400px !important;
        overflow-y: auto !important;
    }
    
    /* Ensure dataframe wrapper doesn't stretch page */
    .stDataFrame {
        max-height: 400px !important;
        overflow-y: auto !important;
    }
    
    /* Table container overflow */
    div[data-testid="stDataFrameContainer"] {
        max-height: 400px !important;
        overflow-y: auto !important;
    }
    
    /* Loading spinner styling */
    .stSpinner > div {
        border-top-color: var(--primary) !important;
    }
    
    /* Enhanced tooltips */
    [data-testid="stTooltip"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--primary) !important;
    }
    
    /* Dark background for map container */
    div[data-testid="stPydeckChart"] {
        background-color: #0a0a1a !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def inject_custom_js() -> None:
    """Inject custom JavaScript for enhanced interactivity."""
    js = """
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Add smooth transitions
        const style = document.createElement('style');
        style.textContent = `
            * {
                transition: background-color 0.3s ease, color 0.3s ease, transform 0.3s ease;
            }
        `;
        document.head.appendChild(style);
        
        // Remove empty skeleton/padding boxes - hide completely so they take zero space
        function collapseEmpty(el) {
            if (!el || el._skeletonRemoved) return;
            el._skeletonRemoved = true;
            el.style.display = 'none';
            el.style.height = '0';
            el.style.minHeight = '0';
            el.style.margin = '0';
            el.style.padding = '0';
            el.style.overflow = 'hidden';
        }
        
        function hasRealContent(node) {
            if (!node) return false;
            const real = node.querySelector(
                'canvas,svg,img,iframe,video,table,pre,code,input,select,textarea,button,' +
                '[data-testid="stMetric"],[data-testid="stDataFrame"],[data-testid="stChart"],[data-testid="stPydeckChart"]'
            );
            if (real) return true;
            const t = (node.textContent || '').replace(/\\s+/g, ' ').trim();
            return t.length > 0;
        }
        
        function removeSkeletonContainers() {
            const sel = '[data-testid="stElementContainer"], [data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"]';
            document.querySelectorAll(sel).forEach((el) => {
                if (el._skeletonRemoved || hasRealContent(el)) return;
                collapseEmpty(el);
            });
        }

        // Run skeleton cleanup immediately and on DOM changes
        removeSkeletonContainers();
        const skeletonObserver = new MutationObserver(removeSkeletonContainers);
        skeletonObserver.observe(document.body, { childList: true, subtree: true });
        
        // Add hover effects to metrics cards
        function addCardHoverEffects() {
            const cards = document.querySelectorAll('.stMetric:not([data-enhanced])');
            cards.forEach(card => {
                card.dataset.enhanced = 'true';
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-2px)';
                    this.style.boxShadow = '0 8px 24px rgba(0, 212, 255, 0.2)';
                });
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                    this.style.boxShadow = 'none';
                });
            });
        }
        
        addCardHoverEffects();
        const cardObserver = new MutationObserver(addCardHoverEffects);
        cardObserver.observe(document.body, { childList: true, subtree: true });
    });
    </script>
    """
    st.markdown(js, unsafe_allow_html=True)
