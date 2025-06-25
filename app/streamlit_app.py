import sys
import os
import locale


if os.name == 'nt':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        locale.setlocale(locale.LC_ALL, 'Turkish_Turkey.utf8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'tr_TR.utf8')
        except locale.Error:
            pass

import streamlit as st
import asyncio
import json
from pathlib import Path
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

from ui.agent_manager import AgentManager
from ui.streamlit_cover_letter_tab import StreamlitCoverLetterTab
from ui.streamlit_linkedin_tab import StreamlitLinkedInTab
from ui.streamlit_resume_tab import StreamlitResumeAnalysisTab
from ui.streamlit_job_file_analysis_tab import StreamlitJobFileAnalysisTab
from ui.streamlit_job_url_analysis_tab import StreamlitJobUrlAnalysisTab
from ui.streamlit_job_compatibility_tab import StreamlitJobCompatibilityTab

from Tool.JobCompatibilityToolkit import JobCompatibilityToolkit
from Tool.CoverLetterToolkit import CoverLetterToolkit

from app.multi_agent.CareerAgentTeamCoordinator import CareerAgentTeamCoordinator

import dotenv

class MultiAgentResultsDisplay:
    
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.base_path = Path("Jobs")
        
    def load_file_content(self, file_path: Path) -> dict:
        try:
            if file_path.exists():
                if file_path.suffix == '.json':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return {
                            "status": "success",
                            "content": json.load(f),
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime)
                        }
                else:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return {
                            "status": "success", 
                            "content": f.read(),
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime)
                        }
            else:
                return {"status": "not_found", "content": None}
        except Exception as e:
            return {"status": "error", "content": str(e)}
    
    def get_quality_score(self, content: dict, file_type: str) -> tuple:
        if not content or content.get("status") != "success":
            return 0, "❌ Dosya okunamadı"
        
        data = content["content"]
        
        if file_type == "job_analysis":
            if isinstance(data, dict) and data.get('note') and 'template' in data['note'].lower():
                return 25, "⚠️ Template veriler"
            score = 0
            checks = [
                (data.get('job_title') and 'belirtilmemiş' not in data['job_title'].lower(), 15),
                (data.get('company_name') and 'belirtilmemiş' not in data['company_name'].lower(), 15),
                (data.get('key_technologies') and len(data['key_technologies']) > 1, 20),
                (data.get('responsibilities') and len(data['responsibilities']) > 1, 20),
                (data.get('qualifications') and len(data['qualifications']) > 1, 15),
                (data.get('location') and 'belirtilmemiş' not in data['location'].lower(), 15)
            ]
            score = sum(points for check, points in checks if check)
            return score, "✅ Yüksek kalite" if score >= 80 else "⚡ Orta kalite" if score >= 60 else "⚠️ Düşük kalite"
            
        elif file_type == "resume_analysis":
            if isinstance(data, dict) and data.get('note') and 'template' in data['note'].lower():
                return 30, "⚠️ Template veriler"
            score = 0
            checks = [
                (data.get('personal_info', {}).get('name') and 'cv\'den okunamadı' not in data['personal_info']['name'].lower(), 20),
                (data.get('experience') and len(data['experience']) > 0, 25),
                (data.get('skills', {}).get('technical') and len(data['skills']['technical']) > 2, 20),
                (data.get('skills', {}).get('soft') and len(data['skills']['soft']) > 2, 15),
                (data.get('education') and len(data['education']) > 0, 20)
            ]
            score = sum(points for check, points in checks if check)
            return score, "✅ Yüksek kalite" if score >= 80 else "⚡ Orta kalite" if score >= 60 else "⚠️ Düşük kalite"
            
        elif file_type == "compatibility":
            score = 0
            checks = [
                (data.get('overall_score') and 'N/A' not in data['overall_score'], 20),
                (data.get('strengths') and len(data['strengths']) > 1, 20),
                (data.get('weaknesses') and len(data['weaknesses']) > 0, 20),
                (data.get('recommendations') and len(data['recommendations']) > 1, 20),
                (data.get('detailed_analysis') and len(data['detailed_analysis']) > 50, 20)
            ]
            score = sum(points for check, points in checks if check)
            return score, "✅ Yüksek kalite" if score >= 80 else "⚡ Orta kalite" if score >= 60 else "⚠️ Düşük kalite"
            
        elif file_type == "cover_letter":
            if isinstance(data, str):
                length = len(data)
                if length < 200:
                    return 40, "⚠️ Çok kısa"
                elif length > 1000:
                    return 85, "✅ Detaylı mektup"
                else:
                    return 70, "⚡ Orta uzunluk"
            return 50, "⚡ Standart format"
        
        return 50, "⚡ Orta kalite"
    
    def display_results(self):
        st.markdown("## 🎉 İş Akışı Tamamlandı!")
        st.markdown(f"**Workflow ID:** `{self.workflow_id}`")
        st.markdown(f"**Tamamlanma Zamanı:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        files_info = {
            "job_analysis": {
                "path": self.base_path / "Job_Analysis" / f"{self.workflow_id}_single_job_analysis.json",
                "icon": "💼",
                "title": "İş Analizi",
                "description": "İş ilanının detaylı analizi ve gereksinimleri"
            },
            "resume_analysis": {
                "path": self.base_path / "Resume_Analysis" / f"{self.workflow_id}_resume_analysis.json", 
                "icon": "📄",
                "title": "CV Analizi",
                "description": "Özgeçmişinizin yapılandırılmış analizi"
            },
            "compatibility": {
                "path": self.base_path / "Job_Compatibility" / f"compatibility_{self.workflow_id}.json",
                "icon": "🎯", 
                "title": "Uygunluk Raporu",
                "description": "İş-CV uyumunun detaylı değerlendirmesi"
            },
            "cover_letter": {
                "path": self.base_path / "Cover_Letters" / f"{self.workflow_id}_cover_letter.txt",
                "icon": "✉️",
                "title": "Kapak Mektubu", 
                "description": "Kişiselleştirilmiş başvuru mektubu"
            }
        }
        
        st.markdown("### 📊 Kalite Özeti")
        quality_cols = st.columns(4)
        
        overall_scores = []
        for i, (file_type, file_info) in enumerate(files_info.items()):
            content = self.load_file_content(file_info["path"])
            score, status = self.get_quality_score(content, file_type)
            overall_scores.append(score)
            
            with quality_cols[i]:
                st.metric(
                    label=f"{file_info['icon']} {file_info['title']}", 
                    value=f"{score}%",
                    delta=status
                )
        
        avg_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0
        if avg_score >= 75:
            st.success(f"🎉 Genel Başarı: **{avg_score:.0f}%** - Mükemmel sonuç!")
        elif avg_score >= 60:
            st.info(f"⚡ Genel Başarı: **{avg_score:.0f}%** - İyi sonuç!")
        else:
            st.warning(f"⚠️ Genel Başarı: **{avg_score:.0f}%** - Gelişim alanları var.")
        
        st.markdown("---")
        
        st.markdown("### 📁 Detaylı Sonuçlar")
        
        for file_type, file_info in files_info.items():
            with st.expander(f"{file_info['icon']} {file_info['title']} - {file_info['description']}", expanded=False):
                content = self.load_file_content(file_info["path"])
                score, status = self.get_quality_score(content, file_type)
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**📄 Dosya:** `{file_info['path'].name}`")
                with col2:
                    if content.get("status") == "success":
                        size_kb = content["size"] / 1024
                        st.write(f"**💾 Boyut:** {size_kb:.1f} KB")
                with col3:
                    if content.get("status") == "success":
                        st.write(f"**🕒 Güncelleme:** {content['modified'].strftime('%H:%M')}")
                
                progress_color = "normal" if score >= 75 else "inverse" if score >= 50 else "off"
                st.progress(score / 100, text=f"Kalite Skoru: {score}% - {status}")
                
                if content.get("status") == "success":
                    if file_type == "cover_letter":
                        st.markdown("**📝 Kapak Mektubu İçeriği:**")
                        st.text_area(
                            label="Kapak Mektubu İçeriği",
                            value=content["content"],
                            height=300,
                            key=f"content_{file_type}",
                            label_visibility="collapsed"
                        )
                    else:
                        st.markdown("**🔍 JSON İçeriği:**")
                        
                        content_data = content["content"]
                        
                        if file_info["path"].suffix == '.json' and not isinstance(content_data, dict):
                            st.error(f"❌ Beklenen JSON dosyası ama string alındı!")
                            st.text(f"Dosya yolu: {file_info['path']}")
                            st.text(f"Veri tipi: {type(content_data)}")
                            st.text(f"İlk 200 karakter: {str(content_data)[:200]}...")
                            return
                        
                        if isinstance(content_data, dict):
                            if file_type == "job_analysis":
                                data = content_data
                                info_col1, info_col2 = st.columns(2)
                                with info_col1:
                                    st.write(f"**🏢 Şirket:** {data.get('company_name', 'Belirtilmemiş')}")
                                    st.write(f"**💼 Pozisyon:** {data.get('job_title', 'Belirtilmemiş')}")
                                    st.write(f"**📍 Konum:** {data.get('location', 'Belirtilmemiş')}")
                                with info_col2:
                                    st.write(f"**🛠️ Teknolojiler:** {len(data.get('key_technologies', []))} adet")
                                    st.write(f"**📋 Sorumluluklar:** {len(data.get('responsibilities', []))} adet")
                                    st.write(f"**🎯 Nitelikler:** {len(data.get('qualifications', []))} adet")
                            
                            elif file_type == "resume_analysis":
                                data = content_data
                                info_col1, info_col2 = st.columns(2)
                                with info_col1:
                                    st.write(f"**👤 İsim:** {data.get('personal_info', {}).get('name', 'Bulunamadı')}")
                                    st.write(f"**🎓 Eğitim:** {len(data.get('education', []))} adet")
                                    st.write(f"**💼 Deneyim:** {len(data.get('experience', []))} adet")
                                with info_col2:
                                    technical_skills = data.get('skills', {}).get('technical', [])
                                    soft_skills = data.get('skills', {}).get('soft', [])
                                    st.write(f"**🔧 Teknik Beceri:** {len(technical_skills)} adet")
                                    st.write(f"**🧠 Soft Beceri:** {len(soft_skills)} adet")
                                    st.write(f"**📊 Projeler:** {len(data.get('projects', []))} adet")
                            
                            elif file_type == "compatibility":
                                data = content_data
                                score_col1, score_col2 = st.columns(2)
                                with score_col1:
                                    st.write(f"**🎯 Genel Skor:** {data.get('overall_score', 'N/A')}")
                                    st.write(f"**🔧 Teknik Skor:** {data.get('technical_skills_score', 'N/A')}")
                                    st.write(f"**💼 Deneyim Skor:** {data.get('experience_score', 'N/A')}")
                                with score_col2:
                                    st.write(f"**🎓 Eğitim Skor:** {data.get('education_score', 'N/A')}")
                                    st.write(f"**💪 Güçlü Yanlar:** {len(data.get('strengths', []))} adet")
                                    st.write(f"**📈 Öneriler:** {len(data.get('recommendations', []))} adet")
                            
                            json_key = f"show_json_{file_type}_{self.workflow_id}"
                            if json_key not in st.session_state:
                                st.session_state[json_key] = False
                            
                            @st.fragment
                            def json_toggle_section(json_data, session_key, file_type_param):
                                current_state = st.session_state.get(session_key, False)
                                
                                if st.button(f"📋 Tam JSON'ı {'Gizle' if current_state else 'Görüntüle'}", key=f"toggle_json_{file_type_param}"):
                                    st.session_state[session_key] = not current_state
                                    st.rerun(scope="fragment")
                                
                                if st.session_state.get(session_key, False):
                                    st.markdown("**📋 Tam JSON İçeriği:**")
                                    try:
                                        with st.expander("📋 JSON Detayları", expanded=True):
                                            st.json(json_data)
                                    except Exception as e:
                                        st.error(f"❌ JSON görüntüleme hatası: {str(e)}")
                                        st.text(f"Ham veri: {str(json_data)[:500]}...")
                            
                            json_toggle_section(content_data, json_key, file_type)
                        else:
                            st.error(f"❌ Beklenen dict veri tipi, alınan: {type(content_data)}")
                            st.text(f"İçerik: {str(content_data)[:200]}...")
                            
                elif content.get("status") == "not_found":
                    st.error("❌ Dosya bulunamadı!")
                else:
                    st.error(f"❌ Dosya okuma hatası: {content.get('content', 'Bilinmeyen hata')}")
                
                st.info(f"📂 **Tam Yol:** `{file_info['path']}`")

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
    
    /* Feature Cards - Modern Design */
    .feature-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 2rem 1.5rem;
        border-radius: var(--border-radius-xl);
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        border: 1px solid var(--gray-200);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        text-align: center;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary-500), var(--primary-600));
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
        background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
        border-color: var(--primary-300);
    }
    
    .feature-card:hover::before {
        opacity: 1;
    }
    
    .feature-icon {
        width: 3.5rem;
        height: 3.5rem;
        background: linear-gradient(135deg, var(--primary-100), var(--primary-200));
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
        font-size: 1.5rem;
        transition: all 0.4s ease;
        box-shadow: 0 4px 14px 0 rgb(59 130 246 / 0.15);
    }
    
    .feature-card:hover .feature-icon {
        background: linear-gradient(135deg, var(--primary-500), var(--primary-600));
        color: white;
        transform: scale(1.1) rotate(5deg);
        box-shadow: 0 8px 25px 0 rgb(59 130 246 / 0.3);
    }
    
    .feature-card h3 {
        color: var(--gray-900);
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: color 0.3s ease;
    }
    
    .feature-card:hover h3 {
        color: var(--primary-700);
    }
    
    .feature-card p {
        color: var(--gray-600);
        font-size: 0.875rem;
        margin: 0;
        line-height: 1.4;
        transition: color 0.3s ease;
    }
    
    .feature-card:hover p {
        color: var(--gray-700);
    }
    
    /* Feature Grid Layout */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    
    /* Responsive for feature cards */
    @media (max-width: 768px) {
        .feature-card {
            height: 160px;
            padding: 1.5rem 1rem;
        }
        
        .feature-icon {
            width: 3rem;
            height: 3rem;
            font-size: 1.3rem;
        }
        
        .feature-card h3 {
            font-size: 1rem;
        }
        
        .feature-card p {
            font-size: 0.8rem;
        }
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
    }
    
    /* Multi-Agent Results Styling */
    .stExpander > details > summary {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 0.5rem;
        padding: 1rem;
        font-weight: 600;
        color: #374151;
    }
    
    .stExpander > details > summary:hover {
        background-color: #f1f5f9;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    
    .stExpander > details[open] > summary {
        background-color: var(--primary-50);
        border-color: var(--primary-200);
        color: var(--primary-700);
    }
    
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 0.75rem;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
        border: 1px solid #e5e7eb;
        transition: all 0.2s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    
    .stProgress .stProgress-bar {
        background: linear-gradient(90deg, var(--primary-500), var(--success-500));
        border-radius: 1rem;
    }
    
    /* Results display improvements */
    .results-summary {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 1px solid #0284c7;
        border-radius: 1rem;
        padding: 2rem;
        margin: 1rem 0;
    }
    
    .quality-indicator {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .quality-high {
        background-color: var(--success-50);
        color: var(--success-600);
        border: 1px solid var(--success-200);
    }
    
    .quality-medium {
        background-color: var(--warning-50);
        color: var(--warning-600);
        border: 1px solid var(--warning-200);
    }
    
    .quality-low {
        background-color: var(--error-50);
        color: var(--error-600);
        border: 1px solid var(--error-200);
    }
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
    help="CV analizi, iş uygunluk değerlendirmesi ve kapak mektubu oluşturma için gereklidir. LinkedIn iş araması için GEREKLI DEĞİLDİR.",
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
    "📊 İş Analizi": "job_file_analysis", 
    "📄 CV Analizi": "resume_analysis",
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
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <h3>LinkedIn İş Arama</h3>
            <p>Akıllı arama ve filtreleme</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <h3>CV Analizi</h3>
            <p>Kapsamlı beceri çıkarımı</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>İş Analizi</h3>
            <p>Gereksinim analizi</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col4, col5, col6 = st.columns(3, gap="large")
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <h3>Uygunluk Testi</h3>
            <p>6 kategoride değerlendirme</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">✉️</div>
            <h3>Kapak Mektubu</h3>
            <p>Kişiselleştirilmiş mektup</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3>Multi-Agent</h3>
            <p>Otomatik başvuru sistemi</p>
        </div>
        """, unsafe_allow_html=True)
    

    


elif selected_page_key == "linkedin_search":
    st.session_state.linkedin_search_tab.create_tab()

elif selected_page_key == "resume_analysis":
    st.session_state.resume_analysis_tab.create_tab()

elif selected_page_key == "job_file_analysis":
    st.session_state.job_file_analysis_tab.create_tab()

elif selected_page_key == "job_compatibility":
    st.session_state.job_compatibility_tab.create_tab()

elif selected_page_key == "cover_letter_generation":
    st.session_state.cover_letter_tab.create_tab()

elif selected_page_key == "multi_agent":
    st.markdown("# 🤖 Multi-Agent Sistemi")
    st.markdown("---")

    if st.session_state.get('workflow_completed', False) and st.session_state.get('last_workflow_id'):
        st.markdown("## 🎉 Son İş Akışı Sonuçları")
        
        if st.button("🔄 Yeni İş Başvurusu Yap", type="secondary"):
            st.session_state.workflow_completed = False
            st.session_state.last_workflow_id = None
            st.rerun()
        
        results_display = MultiAgentResultsDisplay(st.session_state.last_workflow_id)
        results_display.display_results()
        
        st.markdown("---")

    with st.container():
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.5rem; border-radius: 1rem; color: white; margin-bottom: 2rem;">
            <h4 style="color: white; margin-bottom: 1rem;">✨ Otomatik İş Başvuru Sistemi</h4>
            <p style="margin: 0; opacity: 0.95;">
                Tek bir iş ilanı URL'si ve CV'nizi yükleyin. Sistem otomatik olarak <strong>iş analizi</strong>, 
                <strong>CV analizi</strong>, <strong>uygunluk testi</strong> ve <strong>kişiselleştirilmiş kapak mektubu</strong> oluşturacak.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([3, 2])
        
        with col1:
            job_url = st.text_input(
                "🔗 İş İlanı URL'si", 
                placeholder="Örn: https://www.linkedin.com/jobs/view/...",
                help="LinkedIn, Indeed, Kariyer.net veya diğer iş sitelerinden URL yapıştırın"
            )
        
        with col2:
            uploaded_resume = st.file_uploader(
                "📄 CV'nizi Yükleyin", 
                type=["pdf", "docx", "doc", "txt"],
                help="PDF, DOCX veya TXT formatında CV yükleyebilirsiniz"
            )

        if job_url and uploaded_resume:
            st.success("✅ Tüm bilgiler hazır! İş akışını başlatabilirsiniz.")
        elif job_url:
            st.info("📄 CV dosyasını yüklemeyi unutmayın.")
        elif uploaded_resume:
            st.info("🔗 İş ilanı URL'sini girmeyi unutmayın.")
        else:
            st.warning("⚠️ Başlamak için iş ilanı URL'si ve CV dosyası gereklidir.")

        start_button = st.button(
            "🚀 İş Akışını Başlat", 
            type="primary", 
            use_container_width=True,
            disabled=(not job_url or not uploaded_resume)
        )

        if start_button and job_url and uploaded_resume:
            if 'workflow_completed' in st.session_state:
                del st.session_state.workflow_completed
            if 'last_workflow_id' in st.session_state:
                del st.session_state.last_workflow_id
            
            resume_save_path = Path("Jobs/Resumes") / uploaded_resume.name
            resume_save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(resume_save_path, "wb") as f:
                f.write(uploaded_resume.getbuffer())

            progress_bar = st.progress(0)
            status_text = st.empty()
            
            coordinator = CareerAgentTeamCoordinator()
            
            try:
                status_text.info("🔍 İş akışı başlatılıyor...")
                progress_bar.progress(10)
                
                result = asyncio.run(coordinator.run_full_workflow(job_url, str(resume_save_path)))
                
                progress_bar.progress(100)
                status_text.success("✅ İş akışı başarıyla tamamlandı!")
                
                st.session_state.last_workflow_id = coordinator.workflow_id
                st.session_state.workflow_completed = True
                
                results_display = MultiAgentResultsDisplay(coordinator.workflow_id)
                results_display.display_results()

            except Exception as e:
                progress_bar.progress(0)
                status_text.error("❌ İş akışı sırasında hata oluştu!")
                
                st.error(f"**Hata Detayı:** {str(e)}")
                
                with st.expander("🔧 Teknik Detaylar (Debug)"):
                    import traceback
                    st.code(traceback.format_exc())
                
                st.markdown("### 💡 Öneriler:")
                st.markdown("""
                - İş ilanı URL'sinin geçerli olduğundan emin olun
                - CV dosyasının okunabilir formatta olduğunu kontrol edin
                - OpenAI API key'inizin geçerli olduğundan emin olun
                - Internet bağlantınızı kontrol edin
                """)


def main():
    pass


if __name__ == "__main__":
    main()