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
GEMINI_MODEL = "gemini-2.5-flash-lite"

# CSS Styles for Mobile App Simulation
CSS_STYLES = """
<style>
    /* --- MOBILE APP SIMULATION --- */
    
    /* 1. Global Background (The "Desk") */
    .stApp {
        background-color: #263238;
        background-image: radial-gradient(#37474F 1px, transparent 1px);
        background-size: 20px 20px;
    }

    /* 2. The Phone Frame */
    .block-container {
        max-width: 390px !important;
        width: 390px !important;
        background-color: #E0F2F1;
        padding: 2rem 1.5rem 2rem 1.5rem !important;
        margin: auto;
        border: 12px solid #111;
        border-radius: 40px;
        box-shadow: 0 0 0 2px #333, 20px 20px 50px rgba(0,0,0,0.5);
        height: 800px !important;
        overflow-y: auto !important;
        color: #37474F !important;
    }

    /* Hide scrollbar */
    .block-container::-webkit-scrollbar { display: none; }
    .block-container { -ms-overflow-style: none; scrollbar-width: none; }
    
    /* Dark text inside phone */
    .block-container h1, .block-container h2, .block-container h3, .block-container p, .block-container li {
        color: #37474F !important;
    }

    /* 3. Hide Streamlit Elements */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    /* 4. Custom Components */
    .main-header { text-align: center; margin-bottom: 2rem; color: #004D40; }
    
    .question-card {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,196,180, 0.15);
        text-align: center;
        margin: 1rem 0;
        border: 1px solid #B2DFDB;
    }
    
    .score-card {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        color: #333;
    }
    
    /* Buttons - Minty Style */
    .stButton > button {
        background: linear-gradient(135deg, #00C853 0%, #009688 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 30px;
        font-weight: bold;
        width: 100%;
        box-shadow: 0 4px 10px rgba(0, 200, 83, 0.3);
        transition: transform 0.2s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 15px rgba(0, 200, 83, 0.4);
    }

    /* Mint UI Specifics */
    .progress-bg { background: #B2DFDB; }
    .skill-card { border: 1px solid #E0F2F1; }
    
    /* Expanders */
    .streamlit-expanderHeader, div[data-testid="stExpander"] details summary {
        background-color: white !important;
        color: #37474F !important;
        border-radius: 10px;
        border: 1px solid #B2DFDB;
    }
    .streamlit-expanderHeader:hover, div[data-testid="stExpander"] details summary:hover {
        color: #009688 !important;
    }
    .streamlit-expanderContent, div[data-testid="stExpander"] details {
        background-color: white !important;
        color: #37474F !important;
    }
    
    /* Donut Chart */
    .donut-chart { 
        width: 180px; height: 180px;
        position: relative; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto; z-index: 1;
    }
    .donut-inner { 
        width: 140px; height: 140px; 
        background-color: white !important;
        border-radius: 50%;
        position: absolute; top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        z-index: 10;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }
    .overall-score { font-size: 3.5rem; }
    
    /* Progress Dots */
    .progress-dots { display: flex; justify-content: center; gap: 10px; margin-bottom: 1rem; }
    .dot { width: 12px; height: 12px; border-radius: 50%; background-color: #B2DFDB; transition: all 0.3s ease; }
    .dot.active { background-color: #009688; transform: scale(1.3); }
    .dot.completed { background-color: #00C853; }
    
    /* Thinking Animation */
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    .thinking-text { animation: pulse 1.5s infinite; font-size: 1.2rem; color: #009688; text-align: center; }
    
    /* === NEW POLISH === */
    
    /* Tip Card */
    .tip-card {
        background: white;
        border: 1px solid #E0F2F1;
        border-radius: 25px;
        padding: 12px 20px;
        margin: 15px 0;
        display: flex;
        align-items: center;
        gap: 10px;
        box-shadow: 0 2px 8px rgba(0,150,136,0.1);
    }
    .tip-icon { font-size: 1.2rem; }
    .tip-text { color: #546E7A; font-size: 0.95rem; }
    
    /* Enhanced Question Card */
    .question-card {
        background: white;
        padding: 1.8rem;
        border-radius: 24px;
        box-shadow: 0 8px 25px rgba(0,150,136, 0.12);
        text-align: center;
        margin: 1rem 0;
        border: none;
    }
    .question-card p {
        font-size: 1.15rem !important;
        font-weight: 500;
        color: #263238 !important;
        line-height: 1.6;
    }
    
    /* Skill Card Enhancements */
    .skill-card {
        background: white;
        padding: 1.2rem;
        border-radius: 18px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        text-align: center;
        margin-bottom: 1rem;
        border: none;
    }
    .skill-score {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        line-height: 1;
    }
    .skill-label {
        font-size: 0.9rem;
        font-weight: 600;
        color: #78909C;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .progress-bg {
        background: #ECEFF1;
        border-radius: 10px;
        height: 6px;
        width: 100%;
        margin-top: 10px;
        overflow: hidden;
    }
    .progress-fill {
        height: 6px;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    
    /* Suggestion Card Enhancements */
    .suggestion-card {
        background: white;
        padding: 1.2rem;
        border-radius: 18px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        border: none;
    }
    .suggestion-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
    }
    .icon-box {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
    }
    .icon-yellow { background: #FFF8E1; color: #FFA000; }
    .icon-purple { background: #F3E5F5; color: #9C27B0; }
    
    .correction-box {
        background: #FAFAFA;
        padding: 12px;
        border-radius: 12px;
        margin-top: 10px;
        border-left: 3px solid #FFC107;
    }
    
</style>
"""
