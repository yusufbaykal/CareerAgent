import streamlit as st
import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ui.agent_manager import AgentManager
from ui.utils import UIUtils
from cover_letter_agent_all import run_agent as run_cover_letter_agent

class StreamlitCoverLetterTab:
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self.utils = UIUtils()
        self.job_analysis_path = Path("Jobs/Job_Analysis")
        self.resume_analysis_path = Path("Jobs/Resume_Analysis")
        self.cover_letter_path = Path("Jobs/Cover_Letters")
        
        self.job_analysis_path.mkdir(parents=True, exist_ok=True)
        self.resume_analysis_path.mkdir(parents=True, exist_ok=True)
        self.cover_letter_path.mkdir(parents=True, exist_ok=True)

    def _run_async_in_thread(self, coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(coro)
        loop.close()
        return result

    def get_job_analysis_files(self) -> list:
        try:
            if not self.job_analysis_path.exists():
                return ["Henüz iş analizi dosyası yok"]
            
            files = [f.name for f in self.job_analysis_path.glob("*.json")]
            return files if files else ["Henüz iş analizi dosyası yok"]
        except Exception:
            return ["Henüz iş analizi dosyası yok"]
    
    def get_resume_analysis_files(self) -> list:
        try:
            if not self.resume_analysis_path.exists():
                return ["Henüz resume analizi dosyası yok"]
            
            files = [f.name for f in self.resume_analysis_path.glob("*.json")]
            return files if files else ["Henüz resume analizi dosyası yok"]
        except Exception:
            return ["Henüz resume analizi dosyası yok"]

    def get_available_jobs_count(self, job_file: str) -> int:
        if job_file == "Henüz iş analizi dosyası yok" or not job_file:
            return 0
        
        try:
            job_file_path = self.job_analysis_path / job_file
            if not job_file_path.exists():
                return 0
            
            with open(job_file_path, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            
            if isinstance(job_data, dict) and "results" in job_data:
                return len(job_data["results"])
            elif isinstance(job_data, list):
                return len(job_data)
            elif isinstance(job_data, dict) and "result" in job_data:
                return len(job_data["result"])
            elif isinstance(job_data, dict):
                return len(job_data)
            else:
                return 0 
        except Exception:
            return 0

    def generate_cover_letter_from_files(self, job_file: str, resume_file: str, max_jobs: int = 3):
        if job_file == "Henüz iş analizi dosyası yok" or not job_file:
            st.error("❌ Lütfen geçerli bir iş analizi dosyası seçin.")
            return
        
        if resume_file == "Henüz resume analizi dosyası yok" or not resume_file:
            st.error("❌ Lütfen geçerli bir resume analizi dosyası seçin.")
            return
        
        job_file_path = self.job_analysis_path / job_file
        resume_file_path = self.resume_analysis_path / resume_file

        if not job_file_path.exists():
            st.error(f"❌ İş analizi dosyası bulunamadı: {job_file}")
            return
        
        if not resume_file_path.exists():
            st.error(f"❌ Resume analizi dosyası bulunamadı: {resume_file}")
            return

        with st.spinner(f"✍️ {max_jobs} iş ilanı için cover letter oluşturuluyor... Bu biraz zaman alabilir."):
            try:
                job_file_path = str(self.job_analysis_path / job_file)
                resume_file_path = str(self.resume_analysis_path / resume_file)
                
                result = self._run_async_in_thread(run_cover_letter_agent(job_file_path, resume_file_path, max_jobs))
                
                if result.get("success", False):
                    cover_letters = result.get("cover_letters", {})
                    total_jobs = result.get("total_jobs", 0)
                    processed_jobs = result.get("processed_jobs", 0)
                    
                    result_msg = f"✅ **{processed_jobs} adet cover letter başarıyla oluşturuldu!**\n\n"
                    result_msg += f"📂 **İş Analizi:** `{job_file}` ({total_jobs} iş ilanından {processed_jobs} tanesi)\n"
                    result_msg += f"📋 **CV Analizi:** `{resume_file}`\n"
                    result_msg += f"📅 **Tarih:** {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                    
                    st.success(result_msg)
                    
                    if cover_letters:
                        st.markdown("### 📄 Oluşturulan Cover Letter'lar")
                        
                        tab_names = list(cover_letters.keys())
                        if len(tab_names) == 1:
                            cover_letter_data = list(cover_letters.values())[0]
                            st.markdown(f"**🏢 {cover_letter_data['company']} - {cover_letter_data['position']}**")
                            st.text_area("Cover Letter İçeriği:", 
                                       cover_letter_data['content'], 
                                       height=400, 
                                       key="single_cover_letter")
                            st.info(f"📁 Kaydedildi: `{cover_letter_data['file_path']}`")
                        else:
                            tabs = st.tabs([f"🏢 {name}" for name in tab_names])
                            for i, (tab, (job_name, cover_letter_data)) in enumerate(zip(tabs, cover_letters.items())):
                                with tab:
                                    st.text_area("Cover Letter İçeriği:", 
                                               cover_letter_data['content'], 
                                               height=350, 
                                               key=f"cover_letter_{i}")
                                    st.info(f"📁 Kaydedildi: `{cover_letter_data['file_path']}`")
                    
                else:
                    error_msg = result.get("error", "Bilinmeyen hata")
                    st.error(f"❌ Cover letter oluşturulurken hata oluştu: {error_msg}")
                    
            except Exception as e:
                st.error(f"❌ Cover letter oluşturulurken hata oluştu: {str(e)}")
                st.text_area("Hata detayları:", str(e), height=150)

    def create_tab(self):
        st.header("✍️ Cover Letter Oluşturma")
        st.markdown("İş analizi ve CV analizi dosyalarınızı kullanarak özelleştirilmiş cover letter oluşturun.")
        
        col1, col2 = st.columns([2, 1])

        with col1:
            job_files = self.get_job_analysis_files()
            resume_files = self.get_resume_analysis_files()
            
            selected_job_file = st.selectbox(
                "📊 İş Analizi Dosyası Seçin:",
                job_files,
                help="Jobs/Job_Analysis/ klasöründeki dosyalar"
            )
            
            selected_resume_file = st.selectbox(
                "📋 CV Analizi Dosyası Seçin:",
                resume_files,
                help="Jobs/Resume_Analysis/ klasöründeki dosyalar"
            )
            
            available_jobs = self.get_available_jobs_count(selected_job_file)
            
            if available_jobs is None:
                available_jobs = 0
            
            if available_jobs > 0:
                st.info(f"📈 Seçilen dosyada toplam **{available_jobs}** iş ilanı bulunuyor")
                
                max_jobs = st.select_slider(
                    "📝 Kaç tane iş ilanı için cover letter oluşturulsun?",
                    options=list(range(1, min(available_jobs + 1, 11))),
                    value=min(3, available_jobs),
                    help="Daha fazla iş seçmek daha uzun sürecektir"
                )
                
                col_mode1, col_mode2 = st.columns(2)
                with col_mode1:
                    individual_mode = st.checkbox("🎯 Tek tek iş seçimi", 
                                                help="İş ilanlarını tek tek seçmek isterseniz")
                
                if individual_mode:
                    st.markdown("##### 🎯 İş İlanı Seçimi")
                    try:
                        job_file_path = self.job_analysis_path / selected_job_file
                        with open(job_file_path, 'r', encoding='utf-8') as f:
                            job_data = json.load(f)
                        
                        if isinstance(job_data, dict) and "results" in job_data:
                            jobs = []
                            for job_item in job_data["results"]:
                                company_info = job_item.get("company_information", "Bilinmeyen Şirket")
                                if company_info and company_info != "Belirtilmemiş":
                                    company = company_info.split(",")[0].split(".")[0].strip()
                                else:
                                    company = "Bilinmeyen Şirket"
                                
                                position_details = job_item.get("position_details", "Bilinmeyen Pozisyon")
                                if position_details and position_details != "Belirtilmemiş":
                                    position = position_details.split(",")[0].strip()
                                else:
                                    position = "Bilinmeyen Pozisyon"
                                
                                job_obj = {
                                    "company": company,
                                    "position": position,
                                    "analysis": job_item
                                }
                                jobs.append(job_obj)
                        elif isinstance(job_data, list):
                            jobs = job_data
                        elif isinstance(job_data, dict) and "result" in job_data:
                            jobs = job_data["result"]
                        elif isinstance(job_data, dict):
                            jobs = []
                            for job_title, job_details in job_data.items():
                                if " - " in job_title:
                                    position, company = job_title.split(" - ", 1)
                                else:
                                    position = job_title
                                    company = job_details.get("company_information", "Bilinmeyen Şirket")
                                    if company == "Belirtilmemiş":
                                        company = "Bilinmeyen Şirket"
                                
                                job_obj = {
                                    "company": company,
                                    "position": position,
                                    "analysis": job_details
                                }
                                jobs.append(job_obj)
                        else:
                            jobs = []
                        
                        selected_job_indices = []
                        for i, job in enumerate(jobs[:10]):
                            if "analysis" in job:
                                company = job.get("company", f"Şirket_{i+1}")
                                position = job.get("position", f"Pozisyon_{i+1}")
                            elif isinstance(job, dict):
                                company = job.get("company", f"Şirket_{i+1}")
                                position = job.get("position", f"Pozisyon_{i+1}")
                                
                                analysis = job.get("analysis", {})
                                if analysis:
                                    company_info = analysis.get("company_information", "")
                                    if company_info and company_info != "Belirtilmemiş":
                                        company = company_info.split(",")[0].split(".")[0].strip() or company
                                    
                                    position_details = analysis.get("position_details", "")
                                    if position_details and position_details != "Belirtilmemiş":
                                        position = position_details
                            else:
                                company = f"Şirket_{i+1}"
                                position = f"Pozisyon_{i+1}"
                            
                            if st.checkbox(f"🏢 {company} - {position}", key=f"job_select_{i}"):
                                selected_job_indices.append(i)
                        
                        if selected_job_indices:
                            st.success(f"✅ {len(selected_job_indices)} iş ilanı seçildi")
                            max_jobs = len(selected_job_indices)
                        else:
                            st.warning("⚠️ Lütfen en az bir iş ilanı seçin")
                            
                    except Exception as e:
                        st.error(f"❌ İş listesi yüklenirken hata: {str(e)}")
                
            else:
                st.warning("⚠️ Seçilen dosyada iş ilanı bulunamadı")
                max_jobs = 0
            
            button_disabled = (available_jobs == 0 or 
                             selected_job_file == "Henüz iş analizi dosyası yok" or 
                             selected_resume_file == "Henüz resume analizi dosyası yok")
            
            if st.button("✍️ Cover Letter Oluştur", 
                        type="primary", 
                        use_container_width=True,
                        disabled=button_disabled):
                if not button_disabled:
                    self.generate_cover_letter_from_files(selected_job_file, selected_resume_file, max_jobs)