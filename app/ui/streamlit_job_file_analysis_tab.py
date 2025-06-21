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
from job_details_agent import run_file_analysis_agent

class StreamlitJobFileAnalysisTab:
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self.utils = UIUtils()
        self.job_results_path = Path("Jobs/Job_Results")
        self.job_analysis_path = Path("Jobs/Job_Analysis")
        
        self.job_results_path.mkdir(parents=True, exist_ok=True)
        self.job_analysis_path.mkdir(parents=True, exist_ok=True)

    def _run_async_in_thread(self, coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(coro)
        loop.close()
        return result

    def get_job_files(self) -> list:
        try:
            if not self.job_results_path.exists():
                return ["Henüz iş dosyası yok"]
            
            files = [f.name for f in self.job_results_path.glob("*.json")]
            return ["Dosya seçin..."] + sorted(files) if files else ["Henüz iş dosyası yok"]
        except Exception:
            return ["Henüz iş dosyası yok"]

    def get_job_count_from_file(self, file_path: Path) -> int:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            
            if isinstance(job_data, dict) and "results" in job_data:
                return len(job_data["results"])
            elif isinstance(job_data, list):
                return len(job_data)
            else:
                return 0
        except Exception:
            return 0

    def analyze_job_file(self, selected_file, max_jobs=None):
        if selected_file in ["Dosya seçin...", "Henüz iş dosyası yok"] or not selected_file:
            st.error("❌ Lütfen geçerli bir iş dosyası seçin.")
            return

        file_path = self.job_results_path / selected_file

        if not file_path.exists():
            st.error(f"❌ Dosya bulunamadı: {selected_file}")
            return

        job_count_text = f" (İlk {max_jobs} iş)" if max_jobs else " (Tüm işler)"
        
        with st.spinner(f"🔍 '{selected_file}' dosyası analiz ediliyor{job_count_text}..."):
            try:
                full_file_path = str(file_path.absolute())
                
                if max_jobs:
                    analysis_query = f"'{full_file_path}' dosyasındaki iş ilanlarından ilk {max_jobs} tanesini detaylı şekilde analiz et ve sonuçları Jobs/Job_Analysis/ klasörüne kaydet."
                else:
                    analysis_query = f"'{full_file_path}' dosyasındaki tüm iş ilanlarını detaylı şekilde analiz et ve sonuçları Jobs/Job_Analysis/ klasörüne kaydet."
                
                result = self._run_async_in_thread(run_file_analysis_agent(analysis_query))
                
                if result and result.get("success"):
                    search_paths = [
                        (self.job_analysis_path, "*.json"),
                        (self.job_analysis_path, "*analyzed*.json"),
                        (self.job_results_path, "*analyzed*.json"),
                        (self.job_results_path, "*.json")
                    ]
                    
                    all_analysis_files = []
                    for search_path, pattern in search_paths:
                        if search_path.exists():
                            files = list(search_path.glob(pattern))
                            all_analysis_files.extend(files)
                    
                    all_analysis_files = list(set(all_analysis_files))
                    
                    if all_analysis_files:
                        latest_file = max(all_analysis_files, key=lambda x: x.stat().st_ctime)
                        job_count_msg = f" ({max_jobs} iş)" if max_jobs else ""
                        result_msg = f"✅ **İş ilanı analizi tamamlandı{job_count_msg}!**\n\n"
                        result_msg += f"📂 **Kaynak:** `{selected_file}`\n"
                        result_msg += f"📊 **Analiz Dosyası:** `{latest_file.name}`\n"
                        result_msg += f"📅 **Tarih:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                        result_msg += f"💾 Detaylı analiz `{latest_file.parent.name}/` klasörüne kaydedildi."
                        
                        st.success(result_msg)
                        
                        try:
                            with open(latest_file, 'r', encoding='utf-8') as f:
                                analysis_content = json.load(f)
                            
                            st.markdown("### 📊 Analiz Sonucu")
                            if isinstance(analysis_content, list):
                                analyzed_count = len(analysis_content)
                                st.info(f"📈 Toplam **{analyzed_count}** iş ilanı analiz edildi")
                            
                            st.json(analysis_content)
                            
                        except Exception as e:
                            st.warning(f"⚠️ Analiz dosyası okunamadı: {str(e)}")
                    
                    else:
                        result_str = str(result.get("response", "")) if result else ""
                        
                        if "kaydedildi" in result_str or "başarıyla" in result_str.lower():
                            job_count_msg = f" ({max_jobs} iş)" if max_jobs else ""
                            st.success(f"✅ **İş ilanı analizi tamamlandı{job_count_msg}!**")
                            st.info("📋 Analiz sonucu agent tarafından kaydedildi.")
                            
                            all_json_files = []
                            for folder in [self.job_analysis_path, self.job_results_path]:
                                if folder.exists():
                                    files = list(folder.glob("*.json"))
                                    all_json_files.extend(files)
                            
                            if all_json_files:
                                latest_any_file = max(all_json_files, key=lambda x: x.stat().st_ctime)
                                st.info(f"📂 Son oluşturulan dosya: `{latest_any_file.name}`")
                        else:
                            st.warning("⚠️ Analiz tamamlandı ancak sonuç dosyası bulunamadı.")
                        
                        if result.get("response"):
                            with st.expander("🤖 Agent Yanıtı"):
                                st.text_area("Detaylar:", str(result["response"]), height=200)
                
                elif result and not result.get("success"):
                    st.error(f"❌ İş analizi hatası: {result.get('error', 'Bilinmeyen hata')}")
                    
                else:
                    st.error("❌ İş analizi işlemi başarısız oldu.")
                    
            except Exception as e:
                st.error(f"❌ Analiz sırasında hata oluştu: {str(e)}")
                st.text_area("Hata detayları:", str(e), height=150)

    def create_tab(self):
        st.header("📁 LinkedIn Dosya Analizi")
        st.markdown("LinkedIn'den kaydedilmiş iş ilanı dosyalarınızı AI ile toplu analiz edin.")
        
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 📂 Analiz Süreci")
            
            available_files = self.get_job_files()
            selected_file = st.selectbox(
                "İş dosyası seçin:",
                available_files,
                help="Jobs/Job_Results/ klasöründeki dosyaları listeler"
            )
            
            if selected_file not in ["Dosya seçin...", "Henüz iş dosyası yok"]:
                file_path = self.job_results_path / selected_file
                total_jobs = self.get_job_count_from_file(file_path)
                
                if total_jobs > 0:
                    st.info(f"📈 Seçilen dosyada toplam **{total_jobs}** iş ilanı bulunuyor")
                    col_mode1, col_mode2 = st.columns(2)
                    
                    with col_mode1:
                        analysis_mode = st.radio(
                            "📊 Analiz Modu:",
                            ["Tümünü analiz et", "Belirli sayıda analiz et"],
                            help="Analiz edilecek iş sayısını seçin"
                        )
                    
                    max_jobs = None
                    if analysis_mode == "Belirli sayıda analiz et":
                        with col_mode2:
                            max_jobs = st.number_input(
                                "Kaç tane iş analiz edilsin?",
                                min_value=1,
                                max_value=min(total_jobs, 20),
                                value=min(5, total_jobs),
                                step=1,
                                help="Daha az iş seçmek daha hızlı sonuç verir"
                            )
                    button_text = f"🔍 {max_jobs} İş Analiz Et" if max_jobs else f"🔍 Tüm İşleri Analiz Et ({total_jobs})"
                    
                    if st.button(button_text, type="primary", use_container_width=True):
                        self.analyze_job_file(selected_file, max_jobs)
                else:
                    st.warning("⚠️ Seçilen dosyada iş ilanı bulunamadı")
            else:
                if st.button("🔍 Dosyayı Analiz Et", type="primary", use_container_width=True, disabled=True):
                    pass