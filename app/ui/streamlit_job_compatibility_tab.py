import streamlit as st
import os
import json
import asyncio
from pathlib import Path
from datetime import datetime

try:
    from .agent_manager import AgentManager
    from ..job_compatibility_agent import create_job_compatibility_agent
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from ui.agent_manager import AgentManager
    from job_compatibility_agent import create_job_compatibility_agent


class StreamlitJobCompatibilityTab:
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self.job_analysis_path = Path("Jobs/Job_Analysis")
        self.resume_analysis_path = Path("Jobs/Resume_Analysis")
        self.compatibility_results_path = Path("Jobs/Job_Compatibility")

        for path in [self.job_analysis_path, self.resume_analysis_path, self.compatibility_results_path]:
            path.mkdir(parents=True, exist_ok=True)

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
            return ["Dosya seçin..."] + sorted(files) if files else ["Henüz iş analizi dosyası yok"]
        except Exception:
            return ["Henüz iş analizi dosyası yok"]

    def get_resume_analysis_files(self) -> list:
        try:
            if not self.resume_analysis_path.exists():
                return ["Henüz CV analizi dosyası yok"]
            
            files = [f.name for f in self.resume_analysis_path.glob("*.json")]
            return ["Dosya seçin..."] + sorted(files) if files else ["Henüz CV analizi dosyası yok"]
        except Exception:
            return ["Henüz CV analizi dosyası yok"]

    def get_compatibility_reports(self) -> list:
        try:
            if not self.compatibility_results_path.exists():
                return []
            
            files = [f.name for f in self.compatibility_results_path.glob("*.json")]
            return sorted(files, key=lambda x: os.path.getmtime(self.compatibility_results_path / x), reverse=True)
        except Exception:
            return []

    def get_jobs_from_analysis_file(self, file_path: Path) -> list:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            
            if isinstance(job_data, dict) and "results" in job_data:
                jobs = job_data["results"]
            elif isinstance(job_data, list):
                jobs = job_data
            else:
                jobs = []
            
            job_list = []
            for i, job in enumerate(jobs):
                if "analysis" in job:
                    company = job.get("company", "Bilinmeyen Şirket")
                    position = job.get("position", f"Pozisyon {i+1}")
                    analysis = job.get("analysis", {})
                    if analysis:
                        company_info = analysis.get("company_information", "")
                        if company_info and company_info != "Belirtilmemiş":
                            company = company_info.split(",")[0].split(".")[0].strip() or company
                        position_details = analysis.get("position_details", "")
                        if position_details and position_details != "Belirtilmemiş":
                            position = position_details
                else:
                    company = job.get("company", "Bilinmeyen Şirket")
                    position = job.get("position", f"Pozisyon {i+1}")
                
                job_list.append({
                    "index": i,
                    "display_name": f"{company} - {position}",
                    "company": company,
                    "position": position,
                    "data": job
                })
            
            return job_list
        except Exception as e:
            st.error(f"❌ İş listesi alınırken hata: {str(e)}")
            return []

    def analyze_job_compatibility(self, job_analysis_file: str, resume_analysis_file: str, selected_job_index: int = None):
        if job_analysis_file in ["Dosya seçin...", "Henüz iş analizi dosyası yok"] or not job_analysis_file:
            st.error("❌ Lütfen geçerli bir iş analizi dosyası seçin.")
            return
        
        if resume_analysis_file in ["Dosya seçin...", "Henüz CV analizi dosyası yok"] or not resume_analysis_file:
            st.error("❌ Lütfen geçerli bir CV analizi dosyası seçin.")
            return

        job_file_path = self.job_analysis_path / job_analysis_file
        resume_file_path = self.resume_analysis_path / resume_analysis_file

        if not job_file_path.exists():
            st.error(f"❌ İş analizi dosyası bulunamadı: {job_analysis_file}")
            return
        
        if not resume_file_path.exists():
            st.error(f"❌ CV analizi dosyası bulunamadı: {resume_analysis_file}")
            return

        try:
            if selected_job_index is not None:
                jobs_list = self.get_jobs_from_analysis_file(job_file_path)
                if selected_job_index < len(jobs_list):
                    selected_job = jobs_list[selected_job_index]
                    job_info = f"{selected_job['company']} - {selected_job['position']}"
                    analysis_text = f" (Seçilen iş: {job_info})"
                else:
                    st.error("❌ Geçersiz iş seçimi.")
                    return
            else:
                analysis_text = ""

            with st.spinner(f"🔄 İş uygunluğu analizi yapılıyor{analysis_text}..."):
                if selected_job_index is not None:
                    message = (
                        f"Lütfen {job_analysis_file} iş analizi dosyasındaki {selected_job_index + 1}. iş ilanını "
                        f"({selected_job['company']} - {selected_job['position']}) "
                        f"{resume_analysis_file} CV analizi dosyası ile karşılaştırarak uygunluk analizi yap. "
                        f"Adayın bu spesifik işe uygunluğunu 10 üzerinden skorla ve detaylı rapor oluştur."
                    )
                else:
                    message = (
                        f"Lütfen {job_analysis_file} iş analizi dosyası ile {resume_analysis_file} CV analizi dosyasını "
                        f"karşılaştırarak uygunluk analizi yap. Adayın işe uygunluğunu 10 üzerinden skorla ve "
                        f"detaylı rapor oluştur."
                    )
                async def run_compatibility_analysis():
                    agent = await create_job_compatibility_agent()
                    try:
                        await agent.aprint_response(message, stream=False)
                        return "Analiz tamamlandı! Sonuçlar dosyalara kaydedildi."
                    except Exception as e:
                        return f"Analiz sırasında hata oluştu: {str(e)}"
                
                result = self._run_async_in_thread(run_compatibility_analysis())
                
                if "hata" not in result.lower():
                    success_msg = "✅ **İş uygunluğu analizi başarıyla tamamlandı!**"
                    if selected_job_index is not None:
                        success_msg += f"\n🎯 **Analiz Edilen İş:** {job_info}"
                    st.success(success_msg)
                    st.info("📊 Analiz sonuçları aşağıdaki 'Mevcut Raporlar' bölümünden görüntülenebilir.")
                    st.rerun()
                else:
                    st.error(f"❌ {result}")
                
        except Exception as e:
            st.error(f"❌ Analiz sırasında hata oluştu: {str(e)}")

    def display_compatibility_report(self, report_file: str):
        try:
            file_path = self.compatibility_results_path / report_file
            
            with open(file_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            st.markdown("### 📊 Uygunluk Analizi Raporu")
            if "metadata" in report_data:
                metadata = report_data["metadata"]
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"👤 **Aday:** {metadata.get('candidate_name', 'Bilinmiyor')}")
                with col2:
                    st.info(f"💼 **Pozisyon:** {metadata.get('job_title', 'Bilinmiyor')}")
                
                st.caption(f"📅 Analiz Tarihi: {metadata.get('analysis_date', 'Bilinmiyor')}")
            
            if isinstance(report_data.get("analysis"), str):
                st.markdown(report_data["analysis"])
            else:
                st.json(report_data)
                
        except Exception as e:
            st.error(f"❌ Rapor görüntüleme hatası: {str(e)}")

    def create_tab(self):
        st.markdown("# 🎯 İş Uygunluğu Testi")
        st.markdown("İş ilanı analizi ile CV analizinizi karşılaştırarak uygunluk skorunuzu öğrenin.")
        st.markdown("## 🔍 Yeni Uygunluk Analizi")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💼 İş Analizi Dosyası")
            job_files = self.get_job_analysis_files()
            selected_job_file = st.selectbox(
                "İş analizi dosyası seçin:",
                job_files,
                key="job_compatibility_job_file"
            )
            
            if selected_job_file not in ["Dosya seçin...", "Henüz iş analizi dosyası yok"]:
                st.success(f"✅ Seçilen dosya: {selected_job_file}")
                
                job_file_path = self.job_analysis_path / selected_job_file
                jobs_list = self.get_jobs_from_analysis_file(job_file_path)
                
                if jobs_list:
                    st.markdown("#### 🎯 Spesifik İş Seçimi")
                    analysis_mode = st.radio(
                        "Analiz modu:",
                        ["Tüm işleri analiz et", "Tek iş seçimi"],
                        help="Belirli bir iş için analiz yapmak isterseniz 'Tek iş seçimi'ni seçin",
                        key="analysis_mode_radio"
                    )
                    
                    selected_job_index = None
                    if analysis_mode == "Tek iş seçimi":
                        st.info(f"📊 Dosyada toplam **{len(jobs_list)}** iş ilanı bulunuyor")
                        job_options = ["İş seçin..."] + [job["display_name"] for job in jobs_list]
                        selected_job_display = st.selectbox(
                            "Analiz edilecek işi seçin:",
                            job_options,
                            key="individual_job_selector"
                        )
                        
                        if selected_job_display != "İş seçin...":
                            for job in jobs_list:
                                if job["display_name"] == selected_job_display:
                                    selected_job_index = job["index"]
                                    break
                            
                            if selected_job_index is not None:
                                selected_job = jobs_list[selected_job_index]
                                st.success(f"🎯 Seçilen iş: **{selected_job['company']}** - **{selected_job['position']}**")

                                with st.expander("📋 İş Detaylarını Görüntüle"):
                                    job_data = selected_job['data']
                                    
                                    col_detail1, col_detail2 = st.columns(2)
                                    with col_detail1:
                                        st.write("**🏢 Şirket:**", job_data.get("company_information", "Belirtilmemiş"))
                                        st.write("**📊 Deneyim Seviyesi:**", job_data.get("experience_level", "Belirtilmemiş"))
                                        st.write("**🏠 Çalışma Ortamı:**", job_data.get("work_environment", "Belirtilmemiş"))
                                    
                                    with col_detail2:
                                        st.write("**💼 Pozisyon:**", job_data.get("position_details", "Belirtilmemiş"))
                                        st.write("**⏱️ Deneyim Yılı:**", job_data.get("years_of_experience", "Belirtilmemiş"))
                                    
                                    tech_stack = job_data.get("tech_stack", [])
                                    if tech_stack:
                                        st.write("**🔧 Teknik Beceriler:**")
                                        st.write(", ".join(tech_stack))
                    else:
                        st.info(f"📊 Dosyadaki **{len(jobs_list)}** işin tümü analiz edilecek")
        
        with col2:
            st.markdown("### 📄 CV Analizi Dosyası")
            resume_files = self.get_resume_analysis_files()
            selected_resume_file = st.selectbox(
                "CV analizi dosyası seçin:",
                resume_files,
                key="job_compatibility_resume_file"
            )
            
            if selected_resume_file not in ["Dosya seçin...", "Henüz CV analizi dosyası yok"]:
                st.success(f"✅ Seçilen dosya: {selected_resume_file}")
        
        st.markdown("---")
        
        button_disabled = (
            selected_job_file in ["Dosya seçin...", "Henüz iş analizi dosyası yok"] or
            selected_resume_file in ["Dosya seçin...", "Henüz CV analizi dosyası yok"]
        )
        
        if ("analysis_mode_radio" in st.session_state and 
            st.session_state.analysis_mode_radio == "Tek iş seçimi" and
            ("individual_job_selector" not in st.session_state or 
             st.session_state.individual_job_selector == "İş seçin...")):
            button_disabled = True
        
        if ("analysis_mode_radio" in st.session_state and 
            st.session_state.analysis_mode_radio == "Tek iş seçimi"):
            button_text = "🎯 Seçilen İş İçin Uygunluk Analizini Başlat"
        else:
            button_text = "🎯 Tüm İşler İçin Uygunluk Analizini Başlat"
        
        if st.button(button_text, type="primary", use_container_width=True, disabled=button_disabled):
            final_job_index = None
            if ("analysis_mode_radio" in st.session_state and 
                st.session_state.analysis_mode_radio == "Tek iş seçimi"):
                final_job_index = selected_job_index
            
            self.analyze_job_compatibility(selected_job_file, selected_resume_file, final_job_index)
        
        st.markdown("## 📋 Mevcut Uygunluk Raporları")
        
        compatibility_reports = self.get_compatibility_reports()
        
        if compatibility_reports:
            selected_report = st.selectbox(
                "Görüntülemek istediğiniz raporu seçin:",
                ["Rapor seçin..."] + compatibility_reports,
                key="compatibility_report_selector"
            )
            
            if selected_report != "Rapor seçin...":
                self.display_compatibility_report(selected_report)
        else:
            st.info("📝 Henüz uygunluk raporu oluşturulmamış. Yukarıdaki formu kullanarak ilk analizinizi yapın.") 