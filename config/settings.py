"""
Configuration settings for IELTS Speaking Grader.
Contains CSS styles, voice options, and other constants.
"""

# Voice options for TTS
VOICE_OPTIONS = {
    "male": "en-US-ChristopherNeural",
    "female": "en-US-JennyNeural"
}

# Gemini Model
GEMINI_MODEL = "gemini-2.5-flash"

# CSS Styles for Mobile App Simulation
CSS_STYLES = """
<style>
    /* --- MOBILE APP SIMULATION --- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* 1. Global Background (The "Desk") - Clean Off-White */
    .stApp {
        background-color: #FFFFFF; /* Pure White */
        background-image: radial-gradient(#F0F2F6 2px, transparent 2px);
        background-size: 40px 40px;
    }

    /* 2. The Phone Frame */
    .block-container {
        max-width: 390px !important;
        width: 390px !important;
        background-color: #E0F2F1;
        padding: 1.5rem 1rem 1.5rem 1rem !important; /* Tightened padding */
        margin: auto;
        border: 12px solid #111;
        border-radius: 40px;
        box-shadow: 0 0 0 2px #333, 20px 20px 50px rgba(0,0,0,0.5);
        height: 800px !important;
        overflow-y: auto !important;
        color: #263238 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1.15rem; /* Larger base font */
    }

    /* Hide scrollbar */
    .block-container::-webkit-scrollbar { display: none; }
    .block-container { -ms-overflow-style: none; scrollbar-width: none; }
    
    /* Dark text inside phone with increased sizes */
    .block-container h1 { font-size: 2.5rem !important; }
    .block-container h2 { font-size: 2rem !important; }
    .block-container h3 { font-size: 1.6rem !important; }
    .block-container p, .block-container li {
        color: #263238 !important;
        font-size: 1.25rem !important; /* Larger body text */
        line-height: 1.5;
    }

    /* 3. Hide Streamlit Elements */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    /* 4. Shared Components */
    .main-header { text-align: center; margin-bottom: 2rem; color: #004D40; }
    
    /* --- BUTTONS: SLIM & PREMIUM --- */
    .stButton > button {
        width: 85% !important;
        display: block !important;
        margin: 0.5rem auto !important; /* Standardized margin */
        transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        border-radius: 12px !important;
        padding: 0.3rem 1rem !important;
        min-height: 0 !important;
        line-height: 1.3 !important;
    }

    /* PRIMARY (Submit, Next, Start) */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #00C853 0%, #009688 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(0, 200, 83, 0.15) !important;
        border-bottom: 3px solid rgba(0,0,0,0.1) !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 15px rgba(0, 200, 83, 0.25) !important;
        filter: brightness(1.05);
    }

    /* SECONDARY (Restart / Take Again) */
    .stButton > button[kind="secondary"] {
        background: #F8F9FA !important;
        color: #546E7A !important;
        border: 1px solid #CFD8DC !important;
        width: 70% !important;
        font-size: 0.95rem !important;
        box-shadow: none !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: #ECEFF1 !important;
        border-color: #90A4AE !important;
        color: #263238 !important;
    }

    /* --- DEFINITIVE REPLAY BUTTON & SPINNER DESIGN --- */
    .replay-container { display: none; }
    
    div:has(.replay-container) + div .stButton > button {
        width: 44px !important;
        height: 44px !important;
        min-width: 44px !important;
        min-height: 44px !important;
        border-radius: 50% !important;
        background: white !important;
        color: #009688 !important; /* Brand Teal */
        border: 1px solid #B2DFDB !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08) !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 !important;
        position: relative !important;
        top: -12px !important; /* Precision alignment with "Record Answer" */
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        line-height: 0 !important;
        font-size: 1.6rem !important;
    }

    /* KILL ALL INNER BOXES & BACKGROUNDS (No "Blue Square") */
    div:has(.replay-container) + div .stButton > button div,
    div:has(.replay-container) + div .stButton > button div p,
    div:has(.replay-container) + div .stButton > button div[data-testid="stMarkdownContainer"] {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    div:has(.replay-container) + div .stButton > button:hover {
        transform: rotate(180deg) scale(1.1) !important;
        background: linear-gradient(135deg, #00C853 0%, #009688 100%) !important;
        color: white !important;
        border-color: #00C853 !important;
        box-shadow: 0 6px 16px rgba(0, 200, 83, 0.3) !important;
    }

    div:has(.replay-container) + div .stButton > button:active { transform: scale(0.9) !important; }

    /* --- OTHER UI ELEMENTS --- */
    div[data-testid="stVerticalBlock"] > div:has(.stMicRecorder) {
        background: white !important;
        padding: 1rem !important;
        border-radius: 20px !important;
        border: 1px dashed #B2DFDB !important;
        margin-top: 1rem !important;
    }

    /* --- SHARED ELEMENTS --- */
    hr { margin: 0.8rem 0 !important; border: 0.5px solid #B2DFDB !important; opacity: 0.2 !important; }
    h5 { margin-top: 1rem !important; margin-bottom: 0.4rem !important; color: #37474F !important; font-weight: 700 !important; }

    .progress-dots { display: flex; justify-content: center; gap: 10px; margin-bottom: 1rem; }
    .dot { width: 12px; height: 12px; border-radius: 50%; background-color: #B2DFDB; transition: all 0.3s ease; }
    .dot.active { background-color: #009688; transform: scale(1.3); }
    .dot.completed { background-color: #00C853; }
    
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    .thinking-text { animation: pulse 1.5s infinite; font-size: 1.25rem; color: #009688; text-align: center; font-weight: 700; margin-top: -1.2rem !important; margin-bottom: 1.5rem !important; }
    
    /* --- CARD SYSTEM (NO GARBAGE) --- */
    .question-card, .tip-card, .skill-card, .suggestion-card, .transcript-card {
        background: white !important;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        border: none;
    }
    
    .transcript-card {
        margin-top: 15px !important;
        margin-bottom: 2.5rem !important;
        padding: 1.8rem !important;
        border: 1px solid #E0F2F1 !important;
        max-height: 250px;
        overflow-y: auto;
    }

    .question-card { padding: 1.8rem; box-shadow: 0 8px 25px rgba(0,150,136, 0.12); text-align: center; }
    .question-card p { font-size: 1.55rem !important; font-weight: 600; color: #1A1A1A !important; line-height: 1.4; }
    
    /* SUGGESTION CARD: WORLD-CLASS BALANCE (45px Gutter) */
    .suggestion-card { 
        padding: 1.4rem 1.1rem !important; 
        box-shadow: 0 4px 18px rgba(0,0,0,0.06); 
        margin-bottom: 1rem !important; 
    }
    .suggestion-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
    .suggestion-type { font-weight: 800; color: #37474F; font-size: 1.2rem; }
    .suggestion-content { margin-left: 45px !important; } /* Perfect Vertical Stack */
    
    .said-block, .better-block { margin-bottom: 1rem; }
    .said-label, .better-label { font-size: 0.85rem; font-weight: 900; letter-spacing: 1px; margin-bottom: 5px; }
    .said-label { color: #90A4AE; }
    .better-label { color: #00C853; }
    .said-text { color: #455A64; font-size: 1.1rem; font-style: italic; line-height: 1.4; }
    .better-text { color: #1B5E20; font-size: 1.2rem; font-weight: 800; line-height: 1.4; }

    .insight-box { 
        background-color: #F8F9FA !important; 
        padding: 1rem !important; 
        border-radius: 12px !important; 
        margin-top: 1.2rem !important; 
        border-left: 4px solid #FFD54F !important;
        display: flex; gap: 10px;
    }
    .insight-text { color: #37474F; font-size: 1.05rem; line-height: 1.5; }

    .icon-box { 
        width: 32px; height: 32px; min-width: 32px; border-radius: 8px; 
        display: flex; align-items: center; justify-content: center; font-size: 1.1rem;
    }
    .icon-purple { background: #F3E5F5; color: #9C27B0; }
    .icon-yellow { background: #FFF9C4; color: #FBC02D; }

    /* --- DONUT CHART (FIXED SIZE) --- */
    .donut-chart { width: 210px; height: 210px; position: relative; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto; z-index: 1; }
    .donut-inner { width: 168px; height: 168px; background-color: white !important; border-radius: 50%; position: absolute; z-index: 10; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 0 10px rgba(0,0,0,0.05); }
    .overall-score { font-size: 3.5rem !important; font-weight: 900 !important; line-height: 1 !important; margin-bottom: 2px; }
    .overall-label { font-size: 1.2rem !important; font-weight: 700; color: #455A64 !important; opacity: 0.8; }
    
    .tip-card { padding: 18px 24px; display: flex; align-items: center; gap: 15px; border: 1px solid #E0F2F1; margin-bottom: 1.5rem; }
    .tip-text { color: #546E7A; font-size: 1.15rem; font-weight: 500; }
    
    .skill-card { padding: 1rem 0.5rem !important; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
    .skill-score { font-size: 3rem; font-weight: 900; line-height: 1; }
    .skill-label { font-size: 0.9rem; font-weight: 800; color: #455A64; margin-bottom: 6px; text-transform: uppercase; }
    
    div[data-testid="stExpander"] details summary { background-color: white !important; color: #37474F !important; border-radius: 15px; border: 1px solid #CFD8DC; font-size: 1.2rem !important; }

    /* --- SPINNER --- */
    div[data-testid="stSpinner"] > div { border-top-color: #00C853 !important; border-width: 3.5px !important; }
    div[data-testid="stSpinner"] + div { color: #004D40 !important; font-weight: 700 !important; }
</style>
"""
