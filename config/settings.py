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
        padding: 2rem 1.5rem 2rem 1.5rem !important;
        margin: auto;
        border: 12px solid #111;
        border-radius: 40px;
        box-shadow: 0 0 0 2px #333, 20px 20px 50px rgba(0,0,0,0.5);
        height: 800px !important;
        overflow-y: auto !important;
        color: #263238 !important;
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
    
    /* Buttons - Minty Style with Larger Text */
    .stButton > button {
        background: linear-gradient(135deg, #00C853 0%, #009688 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 30px;
        font-weight: bold;
        font-size: 1.3rem !important; /* Larger Button Text */
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
    
    /* Expanders with Larger Headers */
    .streamlit-expanderHeader, div[data-testid="stExpander"] details summary {
        background-color: white !important;
        color: #37474F !important;
        border-radius: 10px;
        border: 1px solid #B2DFDB;
        font-size: 1.25rem !important; /* Larger Expander Header */
    }
    .streamlit-expanderHeader:hover, div[data-testid="stExpander"] details summary:hover {
        color: #009688 !important;
    }
    .streamlit-expanderContent, div[data-testid="stExpander"] details {
        background-color: white !important;
        color: #37474F !important;
        font-size: 1.15rem !important;
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
    .overall-score { font-size: 4rem; font-weight: 800; }
    
    /* Progress Dots */
    .progress-dots { display: flex; justify-content: center; gap: 10px; margin-bottom: 1rem; }
    .dot { width: 12px; height: 12px; border-radius: 50%; background-color: #B2DFDB; transition: all 0.3s ease; }
    .dot.active { background-color: #009688; transform: scale(1.3); }
    .dot.completed { background-color: #00C853; }
    
    /* Thinking Animation */
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    .thinking-text { animation: pulse 1.5s infinite; font-size: 1.5rem; color: #009688; text-align: center; font-weight: 500; }
    
    /* === NEW POLISH === */
    
    /* Tip Card with Larger Text */
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
    .tip-icon { font-size: 1.5rem; }
    .tip-text { color: #546E7A; font-size: 1.2rem; font-weight: 500; line-height: 1.4; }
    
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
        font-size: 1.6rem !important; /* Significantly Larger Question */
        font-weight: 600;
        color: #1A1A1A !important;
        line-height: 1.5;
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
        font-size: 3.2rem;
        font-weight: 900;
        margin: 0;
        line-height: 1;
        color: #00796B;
    }
    .skill-label {
        font-size: 1.1rem;
        font-weight: 700;
        color: #546E7A;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
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
        transition: width 0.7s cubic-bezier(0.4, 0, 0.2, 1);
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
        font-size: 1.3rem;
    }
    .icon-yellow { background: #FFF8E1; color: #FFA000; }
    .icon-purple { background: #F3E5F5; color: #9C27B0; }
    
    .correction-box {
        background: #F5F7F8;
        padding: 12px;
        border-radius: 12px;
        margin-top: 10px;
        border-left: 3px solid #FFC107;
        font-size: 1.15rem !important;
    }
    
</style>
"""
