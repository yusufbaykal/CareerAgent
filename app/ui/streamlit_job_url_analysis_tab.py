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
from job_details_agent import run_agent as run_job_analysis_agent

class StreamlitJobUrlAnalysisTab:
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self.utils = UIUtils()
        self.job_results_path = Path("Jobs/Job_Results")
        
        self.job_results_path.mkdir(parents=True, exist_ok=True)

    def _run_async_in_thread(self, coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(coro)
        loop.close()
        return result

    def analyze_job_url(self, job_url):
        if not job_url or not job_url.strip():
            st.error("❌ Lütfen geçerli bir iş ilanı URL'si girin.")
            return

        if not (job_url.startswith('http://') or job_url.startswith('https://')):
            st.error("❌ Lütfen geçerli bir URL girin (http:// veya https:// ile başlamalı).")
            return

        with st.spinner(f"🔍 İş ilanı analiz ediliyor..."):
            try:
                analysis_query = f"Bu iş ilanı URL'sini analiz et ve sonuçları kaydet: {job_url}"
                result = self._run_async_in_thread(run_job_analysis_agent(analysis_query))
                if result:
                    json_files = list(self.job_results_path.glob("*job*.json"))
                    if json_files:
                        latest_file = max(json_files, key=lambda x: x.stat().st_ctime)
                        result_msg = f"✅ **İş ilanı URL analizi tamamlandı!**\n\n"
                        result_msg += f"🔗 **URL:** `{job_url}`\n"
                        result_msg += f"📊 **Sonuç Dosyası:** `{latest_file.name}`\n"
                        result_msg += f"📅 **Tarih:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                        result_msg += f"💾 Analiz sonucu `Jobs/Job_Results/` klasörüne kaydedildi."
                        
                        st.success(result_msg)
                        try:
                            with open(latest_file, 'r', encoding='utf-8') as f:
                                analysis_content = json.load(f)
                            
                            st.markdown("### 📊 Analiz Sonucu")
                            st.json(analysis_content)
                            
                        except Exception as e:
                            st.info(f"📄 Analiz dosyası oluşturuldu: `{latest_file.name}`")
                    
                    else:
                        st.warning("⚠️ Analiz tamamlandı ancak sonuç dosyası bulunamadı.")
                        st.text_area("Agent Yanıtı:", str(result), height=200)
                else:
                    st.error("❌ URL analizi işlemi başarısız oldu.")
                    
            except Exception as e:
                st.error(f"❌ Analiz sırasında hata oluştu: {str(e)}")
                st.text_area("Hata detayları:", str(e), height=150)

    def create_tab(self):
        st.header("🔗 İş İlanı URL Analizi")
        st.markdown("Herhangi bir iş ilanı URL'sini AI ile analiz edin.")
        
        col1, col2 = st.columns([2, 1])

        with col1:
            job_url = st.text_input(
                "🔗 İş İlanı URL'si",
                placeholder="https://www.linkedin.com/jobs/view/...",
                help="Analiz etmek istediğiniz iş ilanının tam URL'sini girin"
            )
            
            if st.button("🔍 URL'yi Analiz Et", type="primary", use_container_width=True):
                self.analyze_job_url(job_url)