import streamlit as st
import os
import sys

sys.path.append(os.path.dirname(__file__))

from ui.agent_manager import AgentManager
from ui.streamlit_cover_letter_tab import StreamlitCoverLetterTab
from ui.streamlit_linkedin_tab import StreamlitLinkedInTab
from ui.streamlit_resume_tab import StreamlitResumeAnalysisTab
from ui.streamlit_job_file_analysis_tab import StreamlitJobFileAnalysisTab
from ui.streamlit_job_url_analysis_tab import StreamlitJobUrlAnalysisTab
from ui.streamlit_job_compatibility_tab import StreamlitJobCompatibilityTab

st.set_page_config(
    page_title="AgnoAgent - AI Destekli Kariyer Asistanı",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Professional Color Palette */
    :root {
        --primary-50: #eff6ff;
        --primary-100: #dbeafe;
        --primary-500: #3b82f6;
        --primary-600: #2563eb;
        --primary-700: #1d4ed8;
        --primary-900: #1e3a8a;
        
        --gray-50: #f9fafb;
        --gray-100: #f3f4f6;
        --gray-200: #e5e7eb;
        --gray-300: #d1d5db;
        --gray-400: #9ca3af;
        --gray-500: #6b7280;
        --gray-600: #4b5563;
        --gray-700: #374151;
        --gray-800: #1f2937;
        --gray-900: #111827;
        
        --success-50: #ecfdf5;
        --success-500: #10b981;
        --success-600: #059669;
        
        --warning-50: #fffbeb;
        --warning-500: #f59e0b;
        --warning-600: #d97706;
        
        --error-50: #fef2f2;
        --error-500: #ef4444;
        --error-600: #dc2626;
        
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
        
        --border-radius-sm: 0.375rem;
        --border-radius-md: 0.5rem;
        --border-radius-lg: 0.75rem;
        --border-radius-xl: 1rem;
    }
    
    /* Global Overrides */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Typography */
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-weight: 600;
        color: var(--gray-900);
        line-height: 1.25;
    }
    
    .main p, .main li, .main span {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: var(--gray-700);
        line-height: 1.6;
    }
    
    /* Clean layout without hero section */
    .main .block-container {
        padding-top: 1rem;
    }
    

    
    /* Professional Cards */
    .pro-card {
        background: white;
        padding: 1.5rem;
        border-radius: var(--border-radius-lg);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--gray-200);
        margin-bottom: 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        min-height: 220px;
        max-height: 220px;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    
    .pro-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-xl);
        border-color: var(--primary-200);
    }
    
    .pro-card .card-icon {
        width: 2.5rem;
        height: 2.5rem;
        background: var(--primary-100);
        border-radius: var(--border-radius-lg);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
        font-size: 1.3rem;
        transition: all 0.3s ease;
        flex-shrink: 0;
    }
    
    .pro-card h3 {
        color: var(--gray-900);
        margin-bottom: 0.75rem;
        font-size: 1.1rem;
        font-weight: 600;
        min-height: 2.5rem;
        display: flex;
        align-items: center;
    }
    

    
    .pro-card ul {
        list-style: none;
        padding: 0;
        margin: 0;
        flex-grow: 1;
        overflow-y: auto;
    }
    
    .pro-card li {
        color: var(--gray-600);
        margin-bottom: 0.4rem;
        font-size: 0.8rem;
        display: flex;
        align-items: center;
    }
    
    .pro-card li:before {
        content: '✓';
        color: var(--success-500);
        font-weight: 600;
        margin-right: 0.5rem;
        font-size: 0.875rem;
    }
    
    /* Responsive adjustments for smaller screens */
    @media (max-width: 1200px) {
        .pro-card {
            min-height: 200px;
            max-height: 200px;
        }
    }
    
    /* Feature Grid Layout */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    
    /* Sidebar Styling */
    .sidebar-logo {
        text-align: center;
        padding: 0.5rem 0;
        margin-bottom: 0.5rem;
    }
    
    .sidebar-logo h2 {
        color: #1f2937;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    
    .sidebar-logo p {
        color: #6b7280;
        font-size: 0.75rem;
        margin: 0;
        font-weight: 500;
    }
    
    .nav-header {
        color: #374151;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        margin: 0.5rem 0 0.3rem 0;
        text-transform: uppercase;
    }
    
    /* Card hover effects for better UX */
    .pro-card:hover .card-icon {
        background: var(--primary-500);
        color: white;
        transform: scale(1.1);
        transition: all 0.3s ease;
    }
    
    /* Status Messages */
    .status-success {
        background: var(--success-50);
        border: 1px solid var(--success-200);
        color: var(--success-800);
        padding: 1rem;
        border-radius: var(--border-radius-md);
        margin: 1rem 0;
    }
    
    .status-warning {
        background: var(--warning-50);
        border: 1px solid var(--warning-200);
        color: var(--warning-800);
        padding: 1rem;
        border-radius: var(--border-radius-md);
        margin: 1rem 0;
    }
    
    .status-error {
        background: var(--error-50);
        border: 1px solid var(--error-200);
        color: var(--error-800);
        padding: 1rem;
        border-radius: var(--border-radius-md);
        margin: 1rem 0;
    }
    
    /* Sidebar Improvements */
    .css-1d391kg {
        background: var(--gray-50);
        border-right: 1px solid var(--gray-200);
    }
    
    .sidebar-logo {
        text-align: center;
        padding: 1.5rem 1rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid var(--gray-200);
    }
    
    .sidebar-logo h2 {
        color: var(--primary-600);
        margin-bottom: 0.25rem;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    .sidebar-logo p {
        color: var(--gray-500);
        font-size: 0.875rem;
        margin: 0;
    }
    
    .nav-section {
        margin-bottom: 2rem;
    }
    
    .nav-header {
        background: var(--gray-100);
        padding: 0.75rem 1rem;
        border-radius: var(--border-radius-md);
        margin-bottom: 0.75rem;
        font-weight: 600;
        color: var(--gray-700);
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* API Key Section */
    .api-key-section {
        background: linear-gradient(135deg, var(--warning-50) 0%, var(--warning-100) 100%);
        border: 1px solid var(--warning-200);
        border-radius: var(--border-radius-lg);
        padding: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .api-key-section h4 {
        color: var(--warning-800);
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
    }
    
    .api-key-section h4:before {
        content: '🔑';
        margin-right: 0.5rem;
    }
    
    .api-key-section p {
        color: var(--warning-700);
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    .api-key-section small {
        color: var(--warning-600);
        font-size: 0.8rem;
    }
    
    /* Button Improvements */
    .stButton > button {
        background: var(--primary-500);
        color: white;
        border: none;
        border-radius: var(--border-radius-md);
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button:hover {
        background: var(--primary-600);
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    
    /* Footer */
    .pro-footer {
        background: var(--gray-50);
        border-top: 1px solid var(--gray-200);
        border-radius: var(--border-radius-lg);
        padding: 2rem;
        margin-top: 4rem;
        text-align: center;
    }
    
    .pro-footer p {
        color: var(--gray-500);
        margin: 0;
        font-size: 0.9rem;
    }
    
    .pro-footer a {
        color: var(--primary-600);
        text-decoration: none;
        font-weight: 500;
    }
    
    .pro-footer a:hover {
        color: var(--primary-700);
        text-decoration: underline;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .hero-container {
            padding: 2rem 1rem;
        }
        
        .hero-container h1 {
            font-size: 2.5rem;
        }
        
        .stats-grid {
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }
        
        .process-grid {
            grid-template-columns: 1fr;
            gap: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

if 'agent_manager' not in st.session_state:
    st.session_state.agent_manager = AgentManager()

if 'cover_letter_tab' not in st.session_state:
    st.session_state.cover_letter_tab = StreamlitCoverLetterTab(st.session_state.agent_manager)

if 'linkedin_search_tab' not in st.session_state:
    st.session_state.linkedin_search_tab = StreamlitLinkedInTab(st.session_state.agent_manager)

if 'resume_analysis_tab' not in st.session_state:
    st.session_state.resume_analysis_tab = StreamlitResumeAnalysisTab(st.session_state.agent_manager)

if 'job_file_analysis_tab' not in st.session_state:
    st.session_state.job_file_analysis_tab = StreamlitJobFileAnalysisTab(st.session_state.agent_manager)

if 'job_url_analysis_tab' not in st.session_state:
    st.session_state.job_url_analysis_tab = StreamlitJobUrlAnalysisTab(st.session_state.agent_manager)

if 'job_compatibility_tab' not in st.session_state:
    st.session_state.job_compatibility_tab = StreamlitJobCompatibilityTab(st.session_state.agent_manager)

st.sidebar.markdown("""
<div class="sidebar-logo">
    <h2>🚀 CareerAgent</h2>
    <p>AI Career Assistant</p>
</div>
""", unsafe_allow_html=True)

current_api_key = os.getenv('OPENAI_API_KEY', '')
if 'openai_api_key' in st.session_state:
    current_api_key = st.session_state.openai_api_key

api_key_input = st.sidebar.text_input(
    "🔑 OpenAI API Key",
    value=current_api_key,
    type="password",
    help="AI fonksiyonları için gereklidir",
    placeholder="sk-..."
)

if api_key_input:
    st.session_state.openai_api_key = api_key_input
    os.environ['OPENAI_API_KEY'] = api_key_input
    st.sidebar.success("✅ Başarılı!")
else:
    st.sidebar.warning("⚠️ Gereklidir!")

st.sidebar.markdown('<div class="nav-header">🤖 AGENTLAR</div>', unsafe_allow_html=True)

pages = {
    "🏠 Ana Sayfa": "home",
    "💼 LinkedIn": "linkedin_search", 
    "📄 CV Analizi": "resume_analysis",
    "📊 İş Analizi": "job_file_analysis",
    "🔗 URL Analizi": "job_url_analysis",
    "🎯 Uygunluk": "job_compatibility",
    "✉️ Kapak Mektubu": "cover_letter_generation",
    "🤖 Multi-Agent": "multi_agent",
}

selected_page_name = st.sidebar.radio(
    "AGENTLAR",
    list(pages.keys()),
    label_visibility="collapsed"
)
selected_page_key = pages[selected_page_name]

if selected_page_key == "home":
    if not api_key_input:
        st.markdown("""
        <div class="api-key-section">
            <h4>Başlamadan Önce</h4>
            <p>Tüm AI özelliklerini kullanabilmek için <strong>OpenAI API Key</strong>'inizi sol menüden girmeniz gerekmektedir.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("## 🌟 **Özellikler & Yetenekler**")
    st.markdown("---")
    
    col1, col2, col3, col4, col5 = st.columns(5, gap="medium")
    
    with col1:
        st.markdown("""
        <div class="pro-card">
            <div class="card-icon">🔍</div>
            <h3>LinkedIn İş Arama</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="pro-card">
            <div class="card-icon">📄</div>
            <h3>CV Analizi</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="pro-card">
            <div class="card-icon">📊</div>
            <h3>İş Analizi</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="pro-card">
            <div class="card-icon">🎯</div>
            <h3>Uygunluk Testi</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="pro-card">
            <div class="card-icon">✉️</div>
            <h3>Kapak Mektubu</h3>
        </div>
        """, unsafe_allow_html=True)
    

    


elif selected_page_key == "linkedin_search":
    st.session_state.linkedin_search_tab.create_tab()

elif selected_page_key == "resume_analysis":
    st.session_state.resume_analysis_tab.create_tab()

elif selected_page_key == "job_file_analysis":
    st.session_state.job_file_analysis_tab.create_tab()

elif selected_page_key == "job_url_analysis":
    st.session_state.job_url_analysis_tab.create_tab()

elif selected_page_key == "job_compatibility":
    st.session_state.job_compatibility_tab.create_tab()

elif selected_page_key == "cover_letter_generation":
    st.session_state.cover_letter_tab.create_tab()

elif selected_page_key == "multi_agent":
    st.markdown("# 🤖 Multi-Agent Sistemi")
    st.markdown("---")


def main():
    pass


if __name__ == "__main__":
    main()