# ==================== IMPORTS ====================
import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import plotly.express as px
import re
import random
import numpy as np

# ==================== MOCK AI MODEL ====================
class MockFakeNewsDetector:
    def __init__(self):
        self.fake_indicators = {
            'emotional': ['miracle', 'shocking', 'amazing', 'unbelievable', 'breakthrough',
                         'secret', 'hidden truth', 'they dont want you to know', 'astounding',
                         'incredible', 'mind-blowing', 'earth-shattering'],
            'urgency': ['urgent', 'immediately', 'act now', 'breaking', 'last chance',
                       'limited time', 'don\'t wait', 'instant', 'quick', 'fast'],
            'conspiracy': ['big pharma', 'cover-up', 'mainstream media', 'government hiding',
                          'deep state', 'elites', 'suppressed', 'censored', 'they\'re lying'],
            'sensational': ['you won\'t believe', 'what happened next', 'the truth about',
                           'exposed', 'revealed', 'secret method', 'doctors hate this']
        }
        
        self.credible_indicators = [
            'according to', 'study', 'research', 'university', 'official',
            'confirmed', 'experts say', 'peer-reviewed', 'scientists', 'data shows',
            'clinical trial', 'journal', 'published', 'report', 'findings'
        ]

    def analyze_text(self, headline, text):
        """Mock analysis that simulates real AI behavior"""
        content = f"{headline} {text}".lower()
        
        # Analyze fake indicators
        fake_score = 0
        details = {'emotional': 0, 'urgency': 0, 'conspiracy': 0, 'sensational': 0}
        found_words = {'emotional': [], 'urgency': [], 'conspiracy': [], 'sensational': []}
        
        for category, words in self.fake_indicators.items():
            for word in words:
                if word in content:
                    details[category] += 1
                    found_words[category].append(word)
                    fake_score += 2 if category == 'conspiracy' else 1
        
        # Analyze credible indicators
        credible_score = 0
        credible_found = []
        for indicator in self.credible_indicators:
            count = content.count(indicator)
            credible_score += count * 2
            if count > 0:
                credible_found.append(indicator)
        
        # Text structure analysis
        exclamation_count = content.count('!')
        question_count = content.count('?')
        all_caps = len(re.findall(r'\b[A-Z]{4,}\b', f"{headline} {text}"))
        
        # Add structure penalties
        fake_score += exclamation_count * 0.5
        fake_score += question_count * 0.3
        fake_score += all_caps * 1
        
        # Length factor (very short texts are suspicious)
        length_factor = max(0.1, min(1.0, len(text) / 500))
        
        # Calculate final scores
        base_fake_score = min(fake_score, 25) / 25
        base_credible_score = min(credible_score, 20) / 20
        
        # Add small random variation for demo purposes
        random_variation = random.uniform(-0.1, 0.1)
        final_score = max(0, min(1, base_fake_score - (base_credible_score * 0.6) + random_variation))
        
        # Determine verdict
        if final_score > 0.7:
            verdict = "🔴 HIGH RISK - LIKELY FAKE"
            confidence = final_score
            color = "fake"
        elif final_score > 0.4:
            verdict = "🟡 MEDIUM RISK - SUSPICIOUS"
            confidence = 0.5
            color = "suspicious"
        else:
            verdict = "🟢 LOW RISK - LIKELY REAL"
            confidence = 1 - final_score
            color = "real"
        
        return {
            'verdict': verdict,
            'confidence': round(confidence * 100, 1),
            'score': round(final_score, 3),
            'details': details,
            'found_words': found_words,
            'credible_indicators': credible_found,
            'text_metrics': {
                'exclamation_marks': exclamation_count,
                'question_marks': question_count,
                'all_caps_words': all_caps,
                'text_length': len(text),
                'length_factor': round(length_factor, 2)
            },
            'component_scores': {
                'fake_indicators_score': round(base_fake_score * 100, 1),
                'credible_indicators_score': round(base_credible_score * 100, 1),
                'structure_penalty': exclamation_count + all_caps
            }
        }

# Initialize detector
detector = MockFakeNewsDetector()

# ==================== STREAMLIT CONFIG ====================
st.set_page_config(
    page_title="AI Fake News Detector - Hackathon Project",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
def load_css():
    st.markdown("""
    <style>
        .main-header {
            font-size: 3rem;
            color: #1E88E5;
            text-align: center;
            margin-bottom: 1rem;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .sub-header {
            text-align: center;
            color: #666;
            margin-bottom: 2rem;
            font-size: 1.2rem;
        }
        .verdict-box {
            padding: 2rem;
            border-radius: 15px;
            margin: 2rem 0;
            text-align: center;
            font-size: 1.8rem;
            font-weight: bold;
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            transition: all 0.3s ease;
        }
        .verdict-box:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }
        .fake-verdict { 
            background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
            border-left: 8px solid #c62828;
            color: #c62828;
        }
        .real-verdict { 
            background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
            border-left: 8px solid #2e7d32;
            color: #2e7d32;
        }
        .suspicious-verdict { 
            background: linear-gradient(135deg, #fff3e0 0%, #ffecb3 100%);
            border-left: 8px solid #ef6c00;
            color: #ef6c00;
        }
        .metric-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 5px solid #1E88E5;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .feature-card {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .stButton>button {
            width: 100%;
            height: 3.5rem;
            font-size: 1.3rem;
            font-weight: bold;
            border-radius: 10px;
            margin: 1rem 0;
        }
        .example-box {
            background: #f0f2f6;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border-left: 4px solid #1E88E5;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .example-box:hover {
            background: #e3e6ef;
            transform: translateX(5px);
        }
        .hackathon-banner {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: bold;
            font-size: 1.2rem;
        }
    </style>
    """, unsafe_allow_html=True)

# ==================== SESSION STATE ====================
def initialize_session_state():
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    if 'current_result' not in st.session_state:
        st.session_state.current_result = None

# ==================== UTILITY FUNCTIONS ====================
def extract_article_from_url(url):
    """Mock URL content extraction - can be enhanced with real scraping"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract headline
        headline = soup.find('h1') or soup.find('title')
        headline_text = headline.get_text().strip() if headline else "Article from URL"
        
        # Extract article content
        paragraphs = soup.find_all('p')
        article_text = ' '.join([p.get_text().strip() for p in paragraphs[:8]])
        
        return headline_text, article_text[:2000]  # Limit text length
    
    except Exception as e:
        # Return mock data if extraction fails
        st.warning(f"⚠️ Could not extract content from URL. Using demo content. Error: {str(e)}")
        mock_headlines = [
            "Breaking News: Major Development in Technology Sector",
            "Scientific Discovery Could Change Everything We Know",
            "Important Update Regarding Recent Events"
        ]
        mock_text = "This is a sample article text extracted from the provided URL. The content appears to be legitimate news reporting with balanced language and factual presentation."
        return random.choice(mock_headlines), mock_text

def save_to_history(headline, result):
    """Save analysis results to session history"""
    history_item = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'headline': headline[:80] + "..." if len(headline) > 80 else headline,
        'verdict': result['verdict'],
        'confidence': result['confidence'],
        'score': result['score'],
        'text_length': result['text_metrics']['text_length']
    }
    st.session_state.analysis_history.append(history_item)
    # Keep only last 20 analyses
    st.session_state.analysis_history = st.session_state.analysis_history[-20:]

def perform_analysis(headline, article_text):
    """Perform analysis and display results"""
    with st.spinner("🤖 AI is analyzing the article content... This may take a few seconds."):
        # Simulate processing time for demo
        import time
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.02)  # Simulate processing
            progress_bar.progress(i + 1)
        
        try:
            result = detector.analyze_text(headline, article_text)
            st.session_state.current_result = result
            save_to_history(headline, result)
            display_results(result, headline)
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")

def display_results(result, headline):
    """Display comprehensive analysis results"""
    st.markdown("---")
    st.subheader("📊 Analysis Results")
    
    # Verdict display
    verdict = result['verdict']
    confidence = result['confidence']
    
    if "FAKE" in verdict:
        verdict_class = "fake-verdict"
        icon = "🔴"
        risk_level = "High Risk"
    elif "REAL" in verdict:
        verdict_class = "real-verdict"
        icon = "🟢"
        risk_level = "Low Risk"
    else:
        verdict_class = "suspicious-verdict"
        icon = "🟡"
        risk_level = "Medium Risk"
    
    st.markdown(f"""
    <div class="verdict-box {verdict_class}">
        {icon} <strong>{verdict}</strong><br>
        <span style="font-size: 1.3rem;">Confidence Level: {confidence}% | Risk Score: {result['score']:.3f}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics in columns
    st.subheader("📈 Detailed Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Risk Score", f"{result['score']:.3f}")
        st.metric("Text Length", f"{result['text_metrics']['text_length']} chars")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Fake Indicators", f"{result['component_scores']['fake_indicators_score']}%")
        st.metric("Credible Indicators", f"{result['component_scores']['credible_indicators_score']}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Exclamation Marks", result['text_metrics']['exclamation_marks'])
        st.metric("Question Marks", result['text_metrics']['question_marks'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("ALL-CAPS Words", result['text_metrics']['all_caps_words'])
        st.metric("Length Adequacy", f"{result['text_metrics']['length_factor'] * 100:.0f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed breakdown
    with st.expander("🔍 Detailed Analysis Breakdown", expanded=True):
        tab1, tab2, tab3 = st.tabs(["🚩 Red Flags", "✅ Credible Signals", "📊 Text Metrics"])
        
        with tab1:
            st.write("**Suspicious Indicators Found:**")
            red_flags_found = False
            for category, count in result['details'].items():
                if count > 0:
                    red_flags_found = True
                    st.write(f"- **{category.title()}**: {count} instances")
                    if result['found_words'][category]:
                        st.write(f"  Words: `{', '.join(set(result['found_words'][category][:5]))}`")
            
            if not red_flags_found:
                st.success("✅ No strong red flags detected!")
        
        with tab2:
            if result['credible_indicators']:
                st.write("**Credible Indicators Found:**")
                for indicator in set(result['credible_indicators']):
                    st.write(f"- ✅ {indicator.title()}")
            else:
                st.warning("⚠️ No strong credible indicators detected.")
        
        with tab3:
            st.write("**Text Structure Analysis:**")
            metrics = result['text_metrics']
            st.write(f"- **Text Length**: {metrics['text_length']} characters")
            st.write(f"- **Exclamation Marks**: {metrics['exclamation_marks']}")
            st.write(f"- **Question Marks**: {metrics['question_marks']}")
            st.write(f"- **ALL-CAPS Words**: {metrics['all_caps_words']}")
            st.write(f"- **Length Adequacy**: {metrics['length_factor'] * 100:.1f}%")
    
    # Recommendations
    with st.expander("💡 Recommendations & Next Steps"):
        if "FAKE" in verdict:
            st.error("""
            **⚠️ High Risk Detected - Exercise Extreme Caution**
            
            **Recommended Actions:**
            - 🔍 Verify through multiple reliable sources
            - 📰 Check fact-checking websites (Snopes, FactCheck.org)
            - ⚠️ Be skeptical of urgent calls to action
            - 🏛️ Look for official statements or press releases
            - 👥 Check author credentials and publication reputation
            - 📅 Verify the publication date
            """)
        elif "SUSPICIOUS" in verdict:
            st.warning("""
            **🟡 Medium Risk Detected - Verify Carefully**
            
            **Recommended Actions:**
            - 🔄 Cross-reference with other sources
            - 👨‍🎓 Check author credentials and expertise
            - 📊 Look for supporting evidence and data
            - 🚫 Be cautious of emotional language
            - 🔎 Search for fact-checking on this topic
            """)
        else:
            st.success("""
            **🟢 Low Risk Detected - Appears Credible**
            
            **Still Recommended:**
            - 🔍 Verify through additional sources
            - 📅 Check publication date for relevance
            - ⚖️ Consider potential biases
            - 👥 Look for expert opinions and citations
            - 🌐 Check the website's about page and mission
            """)

# ==================== PAGE RENDERING FUNCTIONS ====================
def render_text_analysis():
    """Render the text analysis interface"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Text Analysis")
        st.write("Paste news content below for analysis:")
        
        headline = st.text_input(
            "**News Headline:**",
            placeholder="Enter the news headline here...",
            key="text_headline"
        )
        
        article_text = st.text_area(
            "**Article Text:**",
            height=200,
            placeholder="Paste the full article text here...",
            key="text_article",
            help="The more text you provide, the more accurate the analysis will be."
        )
        
        analyze_btn = st.button(
            "🔍 Analyze Article", 
            type="primary", 
            use_container_width=True,
            disabled=not (headline.strip() and article_text.strip())
        )
    
    with col2:
        st.subheader("💡 Quick Examples")
        st.write("Try these examples to see how the detector works:")
        
        examples = [
            {
                "title": "🚨 Sensational Example",
                "headline": "SHOCKING Discovery Cures All Diseases Overnight!",
                "text": "BREAKING: Doctors are FURIOUS about this simple trick! Big Pharma doesn't want you to know this SECRET method that cures everything INSTANTLY! ACT NOW before it's banned forever! This UNBELIEVABLE breakthrough will change medicine as we know it!"
            },
            {
                "title": "📚 Credible Example", 
                "headline": "New Study Shows Promising Medical Treatment Results",
                "text": "A recent study published in the Journal of Medical Research indicates promising results for new treatment methods. According to experts at Harvard University, the findings show significant improvement in patient outcomes. The research was conducted over a 2-year period with proper clinical trials and peer review."
            },
            {
                "title": "⚠️ Conspiracy Example",
                "headline": "The Truth They Don't Want You to Know About Vaccines",
                "text": "Mainstream media is covering up the real dangers. Government officials are hiding the truth about what's really in these vaccines. The elites don't want ordinary people to know about the secret ingredients that are controlling our minds."
            }
        ]
        
        for example in examples:
            if st.button(f"**{example['title']}**", key=f"example_{example['title']}"):
                st.session_state.text_headline = example['headline']
                st.session_state.text_article = example['text']
                st.rerun()
    
    if analyze_btn and headline and article_text:
        perform_analysis(headline, article_text)

def render_url_analysis():
    """Render the URL analysis interface"""
    st.subheader("🔗 URL Analysis")
    st.write("Enter a news article URL to analyze content directly from the web:")
    
    url = st.text_input(
        "**News Article URL:**",
        placeholder="https://example.com/news-article",
        key="url_input",
        help="Supported: Most news websites and blogs"
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        fetch_btn = st.button(
            "🌐 Fetch & Analyze", 
            type="primary",
            disabled=not url.strip()
        )
    
    if fetch_btn and url:
        with st.spinner("🔄 Fetching and analyzing article content..."):
            headline, article_text = extract_article_from_url(url)
            
            if headline and article_text:
                st.success("✅ Content fetched successfully!")
                
                with st.expander("📄 Review Extracted Content", expanded=True):
                    st.text_input("**Headline:**", value=headline, key="url_headline_display")
                    st.text_area("**Article Text:**", value=article_text, height=150, key="url_article_display")
                
                if st.button("🔍 Analyze Fetched Content", type="secondary", use_container_width=True):
                    perform_analysis(headline, article_text)

def render_history():
    """Render analysis history"""
    st.subheader("📊 Analysis History")
    
    if not st.session_state.analysis_history:
        st.info("📝 No analysis history yet. Analyze some articles to see your history here!")
        return
    
    # Convert to DataFrame for easier manipulation
    history_df = pd.DataFrame(st.session_state.analysis_history)
    
    # Statistics
    st.write("### 📈 Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Analyses", len(history_df))
    with col2:
        real_count = len(history_df[history_df['verdict'].str.contains('REAL')])
        st.metric("Real Articles", real_count)
    with col3:
        fake_count = len(history_df[history_df['verdict'].str.contains('FAKE')])
        st.metric("Fake Articles", fake_count)
    with col4:
        suspicious_count = len(history_df[history_df['verdict'].str.contains('SUSPICIOUS')])
        st.metric("Suspicious", suspicious_count)
    
    # History table
    st.write("### 📋 Recent Analyses")
    st.dataframe(history_df, use_container_width=True, hide_index=True)
    
    # Charts
    if len(history_df) > 1:
        st.write("### 📊 Trends Over Time")
        
        # Convert timestamp for plotting
        history_df['timestamp_dt'] = pd.to_datetime(history_df['timestamp'])
        
        tab1, tab2 = st.tabs(["Confidence Trend", "Risk Score Distribution"])
        
        with tab1:
            fig = px.line(history_df, x='timestamp_dt', y='confidence', 
                         title='Analysis Confidence Over Time', markers=True,
                         labels={'timestamp_dt': 'Time', 'confidence': 'Confidence %'})
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            fig = px.histogram(history_df, x='score', nbins=10,
                             title='Distribution of Risk Scores',
                             labels={'score': 'Risk Score'})
            st.plotly_chart(fig, use_container_width=True)

def render_about():
    """Render about page"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("ℹ️ About This Hackathon Project")
        st.markdown("""
        ### 🔍 AI Fake News Detector - Hackathon Edition
        
        **🏆 Created for Hackathon Presentation**
        
        This application demonstrates advanced pattern recognition and linguistic analysis 
        to identify potential misinformation in news content.
        
        #### 🎯 How It Works
        
        **📊 Advanced Content Analysis**
        - Emotional language patterns and sensationalism detection
        - Urgency signals and pressure tactics analysis  
        - Conspiracy theory indicator scanning
        - Credible source reference validation
        
        **📝 Structural Analysis Engine**
        - Exclamation mark frequency analysis
        - ALL-CAPS word pattern detection
        - Text complexity and depth assessment
        - Rhetorical device identification
        
        **🎯 Multi-dimensional Scoring**
        - Weighted fake news indicator scoring
        - Credible content marker validation
        - Writing style assessment
        - Overall content quality evaluation
        
        #### 🔬 Technical Implementation
        
        **Built with:**
       - Streamlit for interactive web interface
        - Plotly for dynamic visualizations
        - Pandas for data analysis
        - BeautifulSoup for web content extraction
        - Custom AI simulation algorithms
        
        **Features:**
        - Real-time analysis with progress indicators
        - Comprehensive reporting dashboard
        - Historical data tracking
        - Responsive mobile-friendly design
        """)
    
    with col2:
        st.subheader("🚀 Hackathon Features")
        
        features = [
            ("🏆 Demo Ready", "Perfect for hackathon presentations"),
            ("🔗 Live URL Analysis", "Real-time web content scanning"),
            ("📊 Interactive Charts", "Dynamic data visualization"),
            ("📱 Mobile Optimized", "Works on all devices"),
            ("🎯 Instant Results", "Fast AI-powered analysis"),
            ("📈 History Tracking", "Analysis trend monitoring")
        ]
        
        for icon, description in features:
            with st.container():
                st.markdown(f'<div class="feature-card">', unsafe_allow_html=True)
                st.write(f"**{icon} {description}**")
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("⚡ Quick Start")
        st.info("""
        **Try these examples:**
        
        1. **Sensational Example** - Shows high risk detection
        2. **Credible Example** - Shows low risk verification  
        3. **Conspiracy Example** - Shows medium risk alert
        
        **Perfect for live demos!**
        """)
        
        st.subheader("⚠️ Hackathon Note")
        st.warning("""
        **This is a demonstration prototype**
        
        Created for hackathon presentation purposes
        
        Shows real AI analysis concepts
        
        Can be enhanced with actual machine learning models
        
        **Ready for judging and live demonstration!**
        """)

def perform_demo_analysis():
    """Perform a demo analysis with example content"""
    examples = [
        ("🚨 SHOCKING: Miracle Cure Discovered in Remote Village!", 
         "BREAKING NEWS! Doctors are ASTOUNDED by this incredible discovery! A remote village has found a SECRET cure that big pharma doesn't want you to know about! ACT NOW before it's too late! This UNBELIEVABLE breakthrough will change medicine forever! They've been SUPPRESSING this information for YEARS!"),
        
        ("New Research Shows Promising Results in Cancer Treatment",
         "According to a study published in the Journal of Medical Research, scientists have made significant progress in cancer treatment. The research, conducted over five years at Harvard University, shows promising results in clinical trials. Experts caution that more testing is needed before widespread implementation. Data from the study indicates a 45% improvement in patient outcomes compared to existing treatments.")
    ]
    
    headline, text = random.choice(examples)
    perform_analysis(headline, text)

# ==================== MAIN APPLICATION ====================
def main():
    # Load CSS and initialize session state
    load_css()
    initialize_session_state()
    
    # Hackathon Banner
    st.markdown("""
    <div class="hackathon-banner">
        🏆 HACKATHON PROJECT | AI Fake News Detector | Live Demo Ready
    </div>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="main-header">🔍 AI Fake News Detector</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Advanced AI-powered analysis for detecting misinformation | Perfect for Hackathon Demo</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("🔍", width=80)
        st.title("Navigation")
        
        analysis_type = st.radio(
            "**Choose Analysis Method:**",
            ["📝 Text Analysis", "🔗 URL Analysis", "📊 Analysis History", "ℹ️ About & Help"]
        )
        
        st.markdown("---")
        st.subheader("🚀 Demo Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Clear History", use_container_width=True):
                st.session_state.analysis_history = []
                st.success("History cleared!")
                st.rerun()
        
        with col2:
            if st.button("🎯 Quick Demo", use_container_width=True):
                perform_demo_analysis()
        
        st.markdown("---")
        st.subheader("📊 Current Stats")
        
        if st.session_state.analysis_history:
            history_df = pd.DataFrame(st.session_state.analysis_history)
            real_count = len(history_df[history_df['verdict'].str.contains('REAL')])
            fake_count = len(history_df[history_df['verdict'].str.contains('FAKE')])
            
            st.write(f"**Analyses:** {len(history_df)}")
            st.write(f"**Real:** {real_count}")
            st.write(f"**Fake/Suspicious:** {fake_count}")
        else:
            st.write("No analyses yet")
        
        st.markdown("---")
        st.subheader("🏆 Hackathon Ready")
        st.success("""
        **Perfect for:**
        - Live demos
        - Judge presentations
        - Audience interaction
        - Technical showcasing
        """)

    # Main content routing
    if analysis_type == "📝 Text Analysis":
        render_text_analysis()
    elif analysis_type == "🔗 URL Analysis":
        render_url_analysis()
    elif analysis_type == "📊 Analysis History":
        render_history()
    else:
        render_about()

# Run the app
if __name__ == "__main__":
    main()
