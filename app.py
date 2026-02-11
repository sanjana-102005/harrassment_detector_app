import streamlit as st
import pickle
import re
from datetime import datetime
import os

# Import custom modules
from detector import HarassmentDetector
from utils import format_confidence_score, get_severity_color

# Page configuration
st.set_page_config(
    page_title="SafeSpace - Harassment Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .harassment-detected {
        background-color: #ffe6e6;
        border-left: 5px solid #ff4444;
    }
    .no-harassment {
        background-color: #e6f7e6;
        border-left: 5px solid #44ff44;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
    }
    .info-box {
        background-color: #e7f3ff;
        border-left: 5px solid #2196F3;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .sos-button {
        background-color: #ff4444;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize detector
@st.cache_resource
def load_detector():
    return HarassmentDetector()

detector = load_detector()

# Header
st.markdown('<div class="main-header">🛡️ SafeSpace: Harassment Detection System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">A gender-inclusive, AI-powered tool to identify and respond to harassment incidents</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("ℹ️ About SafeSpace")
    st.info("""
    **SafeSpace** helps you:
    - Identify harassment incidents
    - Get legal guidance (India)
    - Access emergency contacts
    - Receive supportive resources
    
    **Gender-Inclusive**: This tool supports all genders equally.
    """)
    
    st.header("🆘 Emergency Contacts (India)")
    st.error("""
    **National Emergency**: 112
    
    **Women's Helpline**: 1091
    
    **Domestic Violence**: 181
    
    **Cyber Crime**: 1930
    
    **Police Control Room**: 100
    
    **Child Helpline**: 1098
    """)
    
    st.header("📋 Supported Categories")
    st.markdown("""
    - Verbal Harassment
    - Physical Harassment
    - Sexual Harassment
    - Cyber Harassment
    - Stalking
    - Workplace Harassment
    - Threats
    - Non-Harassment
    """)

# Main content
tab1, tab2, tab3 = st.tabs(["🔍 Analyze Incident", "📚 Resources", "ℹ️ How It Works"])

with tab1:
    st.header("Describe Your Incident")
    
    # User input
    incident_text = st.text_area(
        "Please describe what happened in your own words:",
        height=150,
        placeholder="Example: My colleague keeps sending me inappropriate messages late at night despite me asking them to stop...",
        help="Be as detailed as you're comfortable being. This information is private and only processed locally."
    )
    
    # Gender selection (optional)
    st.markdown("**Optional**: Share your gender identity (helps us provide better resources)")
    gender = st.selectbox(
        "Gender (Optional)",
        ["Prefer not to say", "Woman", "Man", "Non-binary", "Transgender", "Other"],
        index=0
    )
    
    # Analyze button
    if st.button("🔍 Analyze Incident", type="primary", use_container_width=True):
        if incident_text.strip():
            with st.spinner("Analyzing your incident..."):
                result = detector.analyze_incident(incident_text)
                
                # Display results
                st.markdown("---")
                st.header("📊 Analysis Results")
                
                # Main classification
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    if result['is_harassment']:
                        st.markdown(
                            f'<div class="result-box harassment-detected">'
                            f'<h3>⚠️ Harassment Detected</h3>'
                            f'<p><strong>Category:</strong> {result["category"]}</p>'
                            f'<p><strong>Severity:</strong> {result["severity"]}</p>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f'<div class="result-box no-harassment">'
                            f'<h3>✅ No Harassment Detected</h3>'
                            f'<p>This appears to be a {result["category"]} situation.</p>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                
                with col2:
                    st.metric("Confidence Score", f"{result['confidence_score']:.1%}")
                
                with col3:
                    severity_color = get_severity_color(result['severity'])
                    st.markdown(
                        f'<div style="background-color: {severity_color}; padding: 1rem; border-radius: 5px; text-align: center;">'
                        f'<strong>Severity Level</strong><br>{result["severity"]}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                
                # Explanation
                st.markdown("### 📝 Analysis Explanation")
                st.info(result['explanation'])
                
                # Detected indicators
                if result['indicators']:
                    st.markdown("### 🔍 Detected Indicators")
                    for indicator in result['indicators']:
                        st.warning(f"• {indicator}")
                
                # Response based on severity
                st.markdown("---")
                
                if result['is_harassment'] and result['severity'] in ['High', 'Critical']:
                    # Serious case - provide legal guidance
                    st.markdown("### 🚨 Recommended Actions for Serious Harassment")
                    
                    # SOS Emergency
                    st.markdown(
                        '<div class="sos-button">🆘 If you are in immediate danger, call 112 (National Emergency)</div>',
                        unsafe_allow_html=True
                    )
                    
                    # Legal guidance
                    st.markdown("### ⚖️ Legal Options (India)")
                    legal_info = detector.get_legal_guidance(result['category'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Applicable Laws:**")
                        for law in legal_info['applicable_laws']:
                            st.markdown(f"• {law}")
                    
                    with col2:
                        st.markdown("**Recommended Actions:**")
                        for action in legal_info['actions']:
                            st.markdown(f"• {action}")
                    
                    # Evidence collection
                    st.markdown("### 📸 Evidence Collection Tips")
                    evidence_tips = detector.get_evidence_tips()
                    for tip in evidence_tips:
                        st.success(f"✓ {tip}")
                    
                    # Helplines
                    st.markdown("### 📞 Relevant Helplines")
                    helplines = detector.get_helplines(result['category'])
                    for helpline in helplines:
                        st.info(f"**{helpline['name']}**: {helpline['number']}\n\n{helpline['description']}")
                
                elif result['is_harassment'] and result['severity'] == 'Medium':
                    # Medium severity - balanced approach
                    st.markdown("### 💡 Recommended Actions")
                    st.warning("""
                    This appears to be a concerning situation. Here are some steps you can take:
                    
                    1. **Document Everything**: Keep records of all incidents
                    2. **Set Boundaries**: Clearly communicate that this behavior is unwelcome
                    3. **Seek Support**: Talk to trusted friends, family, or counselors
                    4. **Report Internally**: If workplace-related, contact HR or management
                    5. **Consider Legal Options**: Consult a lawyer if the situation escalates
                    """)
                    
                    # Support resources
                    st.markdown("### 🤝 Support Resources")
                    st.info("""
                    - **National Commission for Women (NCW)**: 7827-170-170
                    - **Legal Services Authority**: Contact your State Legal Services Authority for free legal aid
                    - **Counseling Services**: Reach out to mental health professionals
                    """)
                
                else:
                    # Low severity or no harassment - supportive message
                    st.markdown("### 💚 Supportive Guidance")
                    st.success("""
                    While this situation may not constitute legal harassment, your feelings are valid. Here are some suggestions:
                    
                    - **Communication**: Try having an open conversation about boundaries
                    - **Self-Care**: Take time for activities that help you feel grounded
                    - **Support Network**: Share with trusted friends or family
                    - **Professional Help**: Consider talking to a counselor if you're feeling stressed
                    - **Monitor**: Keep track if the situation changes or escalates
                    """)
                    
                    st.info("""
                    **Remember**: Not all conflicts are harassment, but all your concerns deserve attention.
                    If the situation evolves, feel free to analyze it again.
                    """)
                
                # Privacy reminder
                st.markdown("---")
                st.markdown(
                    '<div class="info-box">'
                    '🔒 <strong>Privacy Note:</strong> Your incident description is processed locally and not stored. '
                    'We recommend keeping your own private record of incidents for documentation purposes.'
                    '</div>',
                    unsafe_allow_html=True
                )
        else:
            st.warning("Please describe your incident in the text box above.")

with tab2:
    st.header("📚 Resources & Information")
    
    st.markdown("### Understanding Harassment")
    
    resource_tabs = st.tabs([
        "Verbal", "Physical", "Sexual", "Cyber", "Stalking", "Workplace", "Threats"
    ])
    
    with resource_tabs[0]:
        st.markdown("""
        **Verbal Harassment** includes:
        - Insults, slurs, or derogatory comments
        - Yelling or screaming
        - Threats or intimidation through words
        - Unwanted comments about appearance, identity, or personal life
        
        **What you can do:**
        - Document the incidents (dates, times, what was said)
        - Set clear boundaries
        - Report to appropriate authorities (workplace, school, police)
        """)
    
    with resource_tabs[1]:
        st.markdown("""
        **Physical Harassment** includes:
        - Unwanted touching or physical contact
        - Hitting, pushing, or shoving
        - Blocking someone's path
        - Destroying personal property
        
        **What you can do:**
        - Ensure your immediate safety first
        - Seek medical attention if injured
        - File a police report (IPC Section 323, 354, etc.)
        - Document injuries with photographs
        """)
    
    with resource_tabs[2]:
        st.markdown("""
        **Sexual Harassment** includes:
        - Unwanted sexual advances or propositions
        - Sexual comments or jokes
        - Sharing explicit content without consent
        - Physical contact of a sexual nature
        
        **Legal Protection (India):**
        - Sexual Harassment of Women at Workplace Act, 2013
        - IPC Section 354A (Sexual Harassment)
        - IPC Section 509 (Word, gesture to insult modesty)
        
        **What you can do:**
        - File a complaint with Internal Complaints Committee (workplace)
        - File an FIR with police
        - Contact National Commission for Women: 7827-170-170
        """)
    
    with resource_tabs[3]:
        st.markdown("""
        **Cyber Harassment** includes:
        - Online bullying or threats
        - Sharing private information (doxxing)
        - Impersonation or fake profiles
        - Revenge porn or non-consensual sharing of images
        
        **Legal Protection (India):**
        - IT Act Section 66A, 66E, 67 (Cyber offenses)
        - IPC Section 354C (Voyeurism)
        - IPC Section 354D (Stalking online)
        
        **What you can do:**
        - Take screenshots of all evidence
        - Report to cybercrime.gov.in
        - Block and report on social media platforms
        - File complaint at nearest Cyber Cell
        - Call Cyber Crime Helpline: 1930
        """)
    
    with resource_tabs[4]:
        st.markdown("""
        **Stalking** includes:
        - Following or monitoring someone
        - Repeated unwanted contact
        - Surveillance or spying
        - Showing up at someone's home or workplace uninvited
        
        **Legal Protection (India):**
        - IPC Section 354D (Stalking)
        
        **What you can do:**
        - Keep a detailed log of all incidents
        - Inform family, friends, and workplace
        - Consider a restraining order
        - File a police complaint
        - Vary your routine and routes
        """)
    
    with resource_tabs[5]:
        st.markdown("""
        **Workplace Harassment** includes:
        - Discrimination based on gender, race, religion, etc.
        - Unfair treatment or exclusion
        - Abuse of power or authority
        - Creating a hostile work environment
        
        **What you can do:**
        - Report to HR or Internal Complaints Committee
        - Document all incidents in writing
        - File complaint with Labour Commissioner
        - Contact State Women's Commission
        - Seek legal counsel if needed
        """)
    
    with resource_tabs[6]:
        st.markdown("""
        **Threats** include:
        - Threats of violence or harm
        - Blackmail or extortion
        - Intimidation tactics
        - Threatening messages or communication
        
        **Legal Protection (India):**
        - IPC Section 503, 504, 506 (Criminal intimidation)
        - IPC Section 383, 384 (Extortion)
        
        **What you can do:**
        - Take threats seriously
        - Report to police immediately
        - Save all evidence (messages, recordings)
        - Inform trusted people about the situation
        - Consider personal safety measures
        """)

with tab3:
    st.header("ℹ️ How SafeSpace Works")
    
    st.markdown("""
    ### 🤖 Our Hybrid Detection System
    
    SafeSpace uses a combination of **rule-based detection** and **machine learning** to analyze incidents:
    
    #### 1️⃣ Rule-Based Analysis
    - Scans for specific keywords and phrases associated with harassment
    - Identifies explicit threats, sexual content, and harmful language
    - Detects patterns indicating repeated unwanted behavior
    
    #### 2️⃣ Machine Learning Classification
    - Uses trained models to understand context and intent
    - Analyzes the overall tone and severity of the incident
    - Reduces false positives by understanding nuance
    
    #### 3️⃣ Intent Prioritization
    We prioritize detection of:
    - **Harmful intent**: Threats, coercion, intimidation
    - **Bad language**: Slurs, insults, derogatory terms
    - **Sexual intent**: Unwanted sexual advances or content
    - **Force/violence**: Physical threats or actions
    - **Repetition**: Patterns of repeated unwanted behavior
    
    ### 📊 Confidence Scoring
    - **90%+**: Very high confidence in classification
    - **70-89%**: High confidence
    - **50-69%**: Moderate confidence (we flag for careful review)
    - **Below 50%**: Low confidence (we err on the side of support)
    
    ### 🎯 Our Approach to Edge Cases
    - When unclear, we provide balanced information rather than making hasty judgments
    - We recognize that context matters and encourage human review
    - We prioritize user safety while minimizing false alarms
    
    ### 🌈 Gender Inclusivity
    SafeSpace is designed to support **all genders equally**:
    - Our training data includes diverse experiences
    - Legal resources provided for everyone
    - Language and examples are gender-neutral where possible
    - We recognize that anyone can experience harassment
    
    ### 🔒 Privacy & Security
    - Your incident descriptions are processed locally
    - No data is stored or transmitted to external servers
    - We recommend you keep your own private documentation
    - This tool is meant to support, not replace, professional help
    
    ### ⚠️ Important Limitations
    - This is an AI tool and can make mistakes
    - It should not replace legal advice from a qualified attorney
    - In emergencies, always contact emergency services immediately
    - Use this tool as one part of your support system
    """)
    
    st.info("""
    **Feedback**: This tool is constantly improving. If you notice any issues or have suggestions,
    please provide feedback to help us make SafeSpace better for everyone.
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
    <p><strong>SafeSpace - Harassment Detection System</strong></p>
    <p>Gender-inclusive • Privacy-focused • Support-oriented</p>
    <p style='font-size: 0.9rem;'>
    ⚠️ This tool provides information and support but is not a substitute for professional legal advice or emergency services.
    </p>
    <p style='font-size: 0.9rem;'>
    In case of emergency, call 112 (India) immediately.
    </p>
    </div>
    """,
    unsafe_allow_html=True
)
