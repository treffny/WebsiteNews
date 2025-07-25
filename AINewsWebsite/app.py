import streamlit as st
import os
from datetime import datetime
import re

# Page configuration
st.set_page_config(
    page_title="Daily AI News Report",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern, clean design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        min-height: 100vh;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Header styling */
    .header-section {
        text-align: center;
        margin-bottom: 2rem;
        padding: 2rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #64748b;
        margin: 1rem 0 0 0;
        font-weight: 400;
    }
    
    .date-display {
        display: inline-block;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 50px;
        font-weight: 600;
        margin-top: 1rem;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    
    /* Control cards */
    .control-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border: 1px solid #f1f5f9;
        transition: all 0.3s ease;
    }
    
    .control-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
        margin: 0 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .card-content {
        color: #64748b;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    .status-badge {
        background: #f0f9ff;
        color: #0369a1;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
        border: 1px solid #bae6fd;
        display: inline-block;
    }
    
    /* News sections */
    .news-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }
    
    .section-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f1f5f9;
    }
    
    .section-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
    }
    
    .section-icon {
        font-size: 1.4rem;
    }
    
    /* News items */
    .news-item {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #3b82f6;
        transition: all 0.3s ease;
        position: relative;
        cursor: pointer;
        text-decoration: none;
        color: inherit;
        display: block;
    }
    
    .news-item:hover {
        background: #f1f5f9;
        transform: translateX(4px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left-color: #1d4ed8;
        text-decoration: none;
        color: inherit;
    }
    
    .news-number {
        position: absolute;
        top: -8px;
        left: -8px;
        background: #3b82f6;
        color: white;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .news-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
        margin: 0 0 0.75rem 0;
        line-height: 1.4;
    }
    
    .news-content {
        color: #475569;
        line-height: 1.6;
        margin-bottom: 0.75rem;
    }
    
    .news-source {
        color: #94a3b8;
        font-size: 0.85rem;
        font-style: italic;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .click-hint {
        color: #3b82f6;
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 0.5rem;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .news-item:hover .click-hint {
        opacity: 1;
    }
    
    /* References section */
    .references-section {
        background: #f8fafc;
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 1rem;
        border: 1px solid #e2e8f0;
    }
    
    .reference-link {
        display: block;
        color: #3b82f6;
        text-decoration: none;
        padding: 0.5rem 0;
        border-bottom: 1px solid #f1f5f9;
        transition: color 0.3s ease;
    }
    
    .reference-link:hover {
        color: #1d4ed8;
    }
    
    /* Footer */
    .footer-section {
        background: #1e293b;
        color: #cbd5e1;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-top: 2rem;
    }
    
    .footer-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: white;
        margin-bottom: 1rem;
    }
    
    .footer-content {
        font-size: 0.9rem;
        line-height: 1.6;
        opacity: 0.8;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.2rem;
        }
        .news-container {
            padding: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
<div class="header-section">
    <h1 class="main-title">AI Intelligence Brief</h1>
    <p class="subtitle">Comprehensive daily insights from 25+ premium AI news sources</p>
    <div class="date-display">📅 Today's Report</div>
</div>
""", unsafe_allow_html=True)

# Control Panel
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="control-card">
        <h3 class="card-title">📊 Report Status</h3>
        <div class="card-content">
    """, unsafe_allow_html=True)
    
    # Show last updated time
    try:
        report_path = "daily_ai_news_report.md"
        if os.path.exists(report_path):
            mod_time = os.path.getmtime(report_path)
            last_updated = datetime.fromtimestamp(mod_time).strftime("%B %d, %Y at %I:%M %p")
            st.markdown(f'<div class="status-badge">Last updated: {last_updated}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-badge">Report pending</div>', unsafe_allow_html=True)
    except:
        st.markdown('<div class="status-badge">Status unknown</div>', unsafe_allow_html=True)
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="control-card">
        <h3 class="card-title">⚙️ Automation</h3>
        <div class="card-content">
            <strong>Schedule:</strong> 1:00 AM London time<br>
            <strong>Email:</strong> raphael.treffny@teleplanforsberg.com<br>
            <strong>Sources:</strong> MIT Tech Review, DeepMind, OpenAI, and 20+ more<br>
            <strong>Status:</strong> <span style="color: #10b981;">Active</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="control-card">
        <h3 class="card-title">📊 Quick Stats</h3>
        <div class="card-content">
            <strong>Sources:</strong> 25+ premium AI news outlets<br>
            <strong>Content:</strong> 10-15 items per section (45 total)<br>
            <strong>Focus:</strong> 40-50% Defense & Security<br>
            <strong>Updates:</strong> <span style="color: #10b981;">Daily at 1 AM</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Load and display content with clickable news items
def parse_and_display_content():
    try:
        with open("daily_ai_news_report.md", "r") as f:
            content = f.read()
        
        lines = content.split('\n')
        current_section = ""
        current_date = ""
        references = {}
        
        # First pass: collect all references
        for line in lines:
            if line.startswith('[Ref') and ']' in line:
                ref_parts = line.split('] ', 1)
                if len(ref_parts) == 2:
                    ref_num = ref_parts[0].replace('[', '').replace('Ref', '')
                    ref_url = ref_parts[1]
                    references[ref_num] = ref_url
        
        # Second pass: display content
        in_section = False
        
        for line in lines:
            if line.startswith('## Date:'):
                current_date = line.replace('## Date:', '').strip()
                
            elif line.startswith('### '):
                if in_section:  # Close previous section
                    st.markdown('</div>', unsafe_allow_html=True)
                
                current_section = line.replace('### ', '').strip()
                
                # Choose icon based on section
                if "General" in current_section:
                    icon = "🤖"
                elif "Defense" in current_section or "Security" in current_section:
                    icon = "🛡️"
                elif "Tools" in current_section or "Innovation" in current_section:
                    icon = "🔧"
                else:
                    icon = "📰"
                
                st.markdown(f"""
                <div class="news-container">
                    <div class="section-header">
                        <span class="section-icon">{icon}</span>
                        <h2 class="section-title">{current_section}</h2>
                    </div>
                """, unsafe_allow_html=True)
                in_section = True
                
            elif line.strip() and line[0].isdigit() and '. **' in line:
                # Parse news item
                parts = line.split('** - ', 1)
                if len(parts) == 2:
                    title_part = parts[0].split('. **', 1)
                    if len(title_part) == 2:
                        number = title_part[0]
                        title = title_part[1]
                        content_part = parts[1]
                        
                        # Extract source and reference
                        source_match = content_part.rfind('(Source: ')
                        ref_match = re.search(r'\[Ref(\d+)\]', content_part)
                        
                        if source_match != -1:
                            content_text = content_part[:source_match].strip()
                            source_text = content_part[source_match:].strip()
                        else:
                            content_text = content_part
                            source_text = ""
                        
                        # Get the reference URL
                        ref_url = "#"
                        if ref_match:
                            ref_num = ref_match.group(1)
                            ref_url = references.get(ref_num, "#")
                        
                        # Create clickable news item
                        st.markdown(f"""
                        <a href="{ref_url}" target="_blank" class="news-item">
                            <div class="news-number">{number}</div>
                            <div class="news-title">{title}</div>
                            <div class="news-content">{content_text}</div>
                            <div class="news-source">{source_text}</div>
                            <div class="click-hint">🔗 Click to read full article</div>
                        </a>
                        """, unsafe_allow_html=True)
                        
            elif line.startswith('## References'):
                if in_section:  # Close current section
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("""
                <div class="news-container">
                    <div class="section-header">
                        <span class="section-icon">📚</span>
                        <h2 class="section-title">References</h2>
                    </div>
                    <div class="references-section">
                """, unsafe_allow_html=True)
                in_section = True
                
            elif line.startswith('[Ref') and ']' in line:
                ref_parts = line.split('] ', 1)
                if len(ref_parts) == 2:
                    ref_num = ref_parts[0] + ']'
                    ref_url = ref_parts[1]
                    st.markdown(f'<a href="{ref_url}" target="_blank" class="reference-link"><strong>{ref_num}</strong> {ref_url}</a>', unsafe_allow_html=True)
        
        # Close any open sections
        if in_section:
            st.markdown('</div></div>', unsafe_allow_html=True)
            
    except FileNotFoundError:
        st.markdown("""
        <div class="news-container">
            <div style="text-align: center; padding: 3rem; color: #64748b;">
                <h2>📄 No Report Available</h2>
                <p>The daily AI news report will be automatically generated at 1:00 AM London time.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.markdown("""
        <div class="news-container">
            <div style="text-align: center; padding: 3rem; color: #64748b;">
                <h2>⚠️ Loading Error</h2>
                <p>Unable to load the report. Please try again later.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Display the content
parse_and_display_content()

# Footer
st.markdown("""
<div class="footer-section">
    <div class="footer-title">🤖 AI Intelligence System</div>
    <div class="footer-content">
        Comprehensive coverage • 45 daily news items • 25+ premium sources<br>
        📧 Newsletter delivery • 🕐 Daily updates at 1 AM • 🔗 Direct article access
    </div>
</div>
""", unsafe_allow_html=True)

