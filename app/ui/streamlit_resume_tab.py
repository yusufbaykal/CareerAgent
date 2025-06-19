import streamlit as st
import os
import shutil
import json
import asyncio
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ui.agent_manager import AgentManager
from ui.utils import UIUtils
from resume_agent import create_resume_analysis_agent

class StreamlitResumeAnalysisTab:
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self.utils = UIUtils()
        self.resume_path = Path("Jobs/Resumes")
        self.analysis_path = Path("Jobs/Resume_Analysis")

        self.resume_path.mkdir(parents=True, exist_ok=True)
        self.analysis_path.mkdir(parents=True, exist_ok=True)

    def _run_async_in_thread(self, coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(coro)
        loop.close()
        return result

    def analyze_resume(self, uploaded_file):
        if uploaded_file is None:
            st.error("❌ Lütfen bir CV dosyası yükleyin.")
            return

        with st.spinner("🔍 CV analiz ediliyor... Bu biraz zaman alabilir."):
            try:
                filename = uploaded_file.name
                saved_path = self.resume_path / filename
                with open(saved_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.info(f"📁 Dosya kaydedildi: {saved_path}")
                agent = self._run_async_in_thread(create_resume_analysis_agent())
                base_name = Path(filename).stem
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                json_filename = f"resume_analysis_{base_name}_{timestamp}.json"
                
                analysis_query = f"""
                Lütfen aşağıdaki adımları takip et:

                1. DOSYA OKUMA: parse_resume tool'unu kullanarak '{filename}' dosyasını oku
                2. ANALIZ: Okunan içeriği detaylı şekilde analiz et
                3. KAYDETME: save_analysis tool'unu kullanarak sonuçları '{json_filename}' dosya adıyla kaydet

                Özgeçmiş dosyası: {filename}
                Analiz sonucu dosyası: {json_filename}

                Analiz şu bilgileri içermeli:
                - Kişisel bilgiler (ad, iletişim)
                - Eğitim geçmişi
                - İş deneyimi
                - Teknik beceriler
                - Yumuşak beceriler
                - Projeler ve başarılar
                - Sertifikalar
                - Dil becerileri
                - Güçlü yönler

                JSON formatında yapılandırılmış sonuç üret.
                """
                                
                st.info("🤖 AI Agent başlatılıyor...")
                
                result = self._run_async_in_thread(agent.arun(analysis_query))
                
                expected_files = list(self.analysis_path.glob(f"resume_analysis_{base_name}_*.json"))
                
                if expected_files:
                    latest_file = max(expected_files, key=lambda x: x.stat().st_ctime)
                    
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        analysis_content = f.read()
                    
                    st.session_state.resume_analysis_result = analysis_content
                    
                    result_msg = f"✅ **CV analizi başarıyla tamamlandı!**\n\n"
                    result_msg += f"📂 **Kaydedilen Dosya:** `{latest_file.name}`\n"
                    result_msg += f"📊 **Analiz Tarihi:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                    result_msg += f"💾 Detaylı CV analizi JSON formatında kaydedildi.\n"
                    result_msg += f"📋 Analiz yetenekler, deneyim, eğitim ve önerileri içermektedir."
                    
                    st.success(result_msg)
                    
                    st.markdown("### 📊 Analiz Sonucu")
                    try:
                        analysis_json = json.loads(analysis_content)
                        st.json(analysis_json)
                    except json.JSONDecodeError:
                        st.text_area("Analiz Sonucu (Metin)", analysis_content, height=300)
                
                else:
                    result_str = str(result) if result else "Boş yanıt"
                    
                    st.warning("⚠️ Analiz dosyası oluşturulamadı.")
                    st.text_area("Agent Yanıtı:", result_str, height=200)
                    
                    if result_str and result_str != "Boş yanıt":
                        fallback_file = self.analysis_path / json_filename
                        
                        fallback_data = {
                            "status": "partial",
                            "message": "Agent yanıtı olarak kaydedildi",
                            "content": result_str,
                            "timestamp": datetime.now().isoformat(),
                            "original_file": filename
                        }
                        
                        with open(fallback_file, 'w', encoding='utf-8') as f:
                            json.dump(fallback_data, f, ensure_ascii=False, indent=2)
                        
                        st.info(f"📝 Agent yanıtı {fallback_file.name} olarak kaydedildi.")
                        st.session_state.resume_analysis_result = json.dumps(fallback_data, ensure_ascii=False, indent=2)
                    
            except Exception as e:
                st.error(f"❌ Hata oluştu: {str(e)}")
                st.text_area("Hata detayları:", str(e), height=150)
                
                if 'resume_analysis_result' in st.session_state:
                    del st.session_state.resume_analysis_result

    def create_tab(self):
        st.header("📋 CV Analizi")
        st.markdown("CV'nizi yükleyin ve AI destekli detaylı analiz alın.")
        
        col1, col2 = st.columns([2, 1])

        with col1:
            uploaded_file = st.file_uploader(
                label="📎 CV Dosyası Yükle",
                type=["pdf", "doc", "docx", "txt"],
                help="PDF, Word veya Metin formatında CV dosyanızı yükleyin."
            )
            
            if st.button("🔍 CV'yi Analiz Et", type="primary", use_container_width=True):
                self.analyze_resume(uploaded_file)