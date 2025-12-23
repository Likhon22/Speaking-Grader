"""
UI Helper Components for IELTS Speaking Grader.
Contains reusable display functions.
"""
import streamlit as st


def render_progress_dots(current: int, total: int) -> str:
    """Generate HTML for progress dots."""
    dots_html = '<div class="progress-dots">'
    for i in range(total):
        if i < current:
            dots_html += '<div class="dot completed"></div>'
        elif i == current:
            dots_html += '<div class="dot active"></div>'
        else:
            dots_html += '<div class="dot"></div>'
    dots_html += '</div>'
    return dots_html


def display_results(result: dict):
    """Display the grading results with the premium Minty UI."""
    if not result:
        return
    
    try:
        overall_score = float(result['FINAL_OVERALL_BAND_SCORE'])
        overall_percent = (overall_score / 9.0) * 100
    except:
        overall_score = 0.0
        overall_percent = 0
    
    # Determine status based on score
    if overall_score >= 8.0:
        status_label = "✨ Excellent work!"
        status_color = "#00C853"
        status_bg = "#E8F5E9"
    elif overall_score >= 6.5:
        status_label = "🌟 Very Good!"
        status_color = "#2962FF"
        status_bg = "#E3F2FD"
    elif overall_score >= 5.0:
        status_label = "👍 Good Effort"
        status_color = "#FFAB00"
        status_bg = "#FFF8E1"
    elif overall_score >= 4.0:
        status_label = "📚 Getting There"
        status_color = "#FF9100"
        status_bg = "#FFF3E0"
    elif overall_score >= 3.0:
        status_label = "🌱 Foundation Building"
        status_color = "#FF3D00"
        status_bg = "#FFEBEE"
    else:
        status_label = "💪 Don't Give Up!"
        status_color = "#D50000"
        status_bg = "#FFEBEE"
    
    scores = result['SCORE_BREAKDOWN']
    
    # --- Overall Score Section ---
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0;">
        <div class="donut-chart" style="background: conic-gradient({status_color} var(--p), #E0F2F1 0); --p: {overall_percent}%;">
            <div class="donut-inner">
                <div class="overall-score" style="color: {status_color};">{overall_score}</div>
                <div class="overall-label">Band Score</div>
            </div>
        </div>
        <div style="margin-top: 20px;">
            <span style="background: {status_bg}; color: {status_color}; padding: 8px 20px; border-radius: 20px; font-weight: bold; font-size: 1.1rem;">
                {status_label}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Skills Breakdown")
    
    # --- Skills Grid ---
    col1, col2 = st.columns(2)
    
    metrics = [
        ("Pronunciation", scores.get('Pronunciation', 0)),
        ("Grammar", scores.get('Grammatical_Range_Accuracy', 0)),
        ("Vocabulary", scores.get('Lexical_Resource', 0)),
        ("Fluency", scores.get('Fluency_Coherence', 0)),
    ]
    
    for i, (label, score) in enumerate(metrics):
        try:
            score = float(score)
            percent = (score / 9.0) * 100
            color = "#00C853" if score >= 7 else "#FFAB00" if score >= 5 else "#FF3D00"
        except:
            score = 0
            percent = 0
            color = "#ddd"

        col = col1 if i % 2 == 0 else col2
        with col:
            st.markdown(f"""
            <div class="skill-card">
                <div class="skill-score" style="color: {color};">{score}</div>
                <div class="skill-label">{label}</div>
                <div class="progress-bg">
                    <div class="progress-fill" style="width: {percent}%; background: {color};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    # --- Suggestions Section ---
    st.markdown("### 💡 Suggestions")
    
    errors = result.get('LANGUAGE_ERRORS', [])
    if errors:
        for err in errors:
            type_label = err.get('error_type', 'Tip')
            icon_class = "icon-purple" if "Pronunciation" in type_label else "icon-yellow"
            icon_symbol = "✨" if "Pronunciation" in type_label else "⚠️"
            explanation = err.get('explanation', "Here is a better way to say it.")
            
            st.markdown(f"""
            <div class="suggestion-card">
                <div class="suggestion-header">
                    <div class="icon-box {icon_class}">{icon_symbol}</div>
                    <div class="suggestion-type">{type_label}</div>
                </div>
                <div class="suggestion-content">
                    <div class="said-block">
                        <div class="said-label">YOU SAID</div>
                        <div class="said-text">"{err.get('original_phrase', '')}"</div>
                    </div>
                    <div class="better-block">
                        <div class="better-label">BETTER</div>
                        <div class="better-text">"{err.get('correction', '')}"</div>
                    </div>
                    <div class="insight-box">
                        <span class="insight-icon">💡</span>
                        <span class="insight-text">{explanation}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No specific errors found! Great job.")
        
    # --- Detailed Report Expander ---
    with st.expander("📄 View Detailed Transcript Analysis"):
        st.markdown("### 📝 Full Transcript & Notes")
        st.write(result.get('POSITIVE_FEEDBACK'))
        st.write(result.get('CRITICAL_FEEDBACK'))
        st.markdown("---")
        st.write(result.get('BAND_UPGRADE_TIP'))
