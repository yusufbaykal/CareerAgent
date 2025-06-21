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
from job_agent_extenction import run_agent as run_linkedin_agent

class StreamlitLinkedInTab:
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self.utils = UIUtils()
        self.job_results_path = Path("Jobs/Job_Results")

        self.job_results_path.mkdir(parents=True, exist_ok=True)

    def _add_custom_css(self):
        st.markdown("""
        <style>
            /* Professional LinkedIn Search Theme */
            .linkedin-hero {
                background: linear-gradient(135deg, #0077B5 0%, #004471 100%);
                padding: 3rem 2rem;
                border-radius: 1rem;
                color: white;
                text-align: center;
                margin-bottom: 2rem;
                box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
                position: relative;
                overflow: hidden;
            }
            
            .linkedin-hero::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.03' fill-rule='evenodd'%3E%3Cpath d='M0 0h40v40H0V0zm20 20c0-11.046 8.954-20 20-20s20 8.954 20 20-8.954 20-20 20S20 31.046 20 20z'/%3E%3C/g%3E%3C/svg%3E");
                z-index: 1;
            }
            
            .linkedin-hero-content {
                position: relative;
                z-index: 2;
            }
            
            .linkedin-hero h1 {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 1rem;
                color: white;
            }
            
            .linkedin-hero p {
                font-size: 1.1rem;
                opacity: 0.95;
                margin: 0;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
            }
            
            .search-form-pro {
                background: white;
                padding: 2.5rem;
                border-radius: 1rem;
                box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
                border: 1px solid #e5e7eb;
                margin-bottom: 2rem;
            }
            
            .search-form-pro h3 {
                color: #1f2937;
                margin-bottom: 1.5rem;
                font-size: 1.5rem;
                font-weight: 600;
                display: flex;
                align-items: center;
            }
            
            .search-form-pro h3:before {
                content: '🔍';
                margin-right: 0.5rem;
                font-size: 1.2rem;
            }
            
            .info-card-pro {
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border: 1px solid #e2e8f0;
                padding: 2rem;
                border-radius: 1rem;
                margin-bottom: 1.5rem;
                transition: all 0.3s ease;
            }
            
            .info-card-pro:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
            }
            
            .info-card-pro h4 {
                color: #0077B5;
                margin-bottom: 1rem;
                font-size: 1.2rem;
                font-weight: 600;
                display: flex;
                align-items: center;
            }
            
            .info-card-pro h4:before {
                content: attr(data-icon);
                margin-right: 0.5rem;
                font-size: 1.1rem;
            }
            
            .info-card-pro ul {
                margin: 0;
                padding: 0;
                list-style: none;
            }
            
            .info-card-pro li {
                margin-bottom: 0.5rem;
                color: #4b5563;
                display: flex;
                align-items: center;
                font-size: 0.9rem;
            }
            
            .info-card-pro li:before {
                content: '✓';
                color: #10b981;
                font-weight: 600;
                margin-right: 0.5rem;
                font-size: 0.8rem;
            }
            
            .search-tips-pro {
                background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                color: white;
                padding: 2rem;
                border-radius: 1rem;
                margin-top: 1.5rem;
                box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
            }
            
            .search-tips-pro h4 {
                margin-bottom: 1rem;
                font-size: 1.2rem;
                font-weight: 600;
                display: flex;
                align-items: center;
            }
            
            .search-tips-pro h4:before {
                content: '💡';
                margin-right: 0.5rem;
            }
            
            .search-tips-pro p {
                margin: 0.5rem 0;
                font-size: 0.9rem;
                opacity: 0.95;
                line-height: 1.5;
            }
            
            .results-pro {
                background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
                border: 1px solid #10b981;
                padding: 2rem;
                border-radius: 1rem;
                margin-top: 2rem;
                box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            }
            
            .results-pro h4 {
                color: #065f46;
                margin-bottom: 1rem;
                font-size: 1.3rem;
                font-weight: 600;
                display: flex;
                align-items: center;
            }
            
            .results-pro h4:before {
                content: '✅';
                margin-right: 0.5rem;
            }
            
            .metric-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 1rem;
                margin: 1.5rem 0;
            }
            
            .metric-card-pro {
                background: white;
                padding: 1.5rem;
                border-radius: 0.75rem;
                text-align: center;
                box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
                border: 1px solid #e5e7eb;
                transition: all 0.3s ease;
            }
            
            .metric-card-pro:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
            }
            
            .metric-number-pro {
                font-size: 2rem;
                font-weight: 700;
                color: #0077B5;
                display: block;
                margin-bottom: 0.5rem;
            }
            
            .metric-label-pro {
                font-size: 0.875rem;
                color: #6b7280;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            
            .status-pro {
                background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
                border: 1px solid #93c5fd;
                padding: 1.5rem;
                border-radius: 1rem;
                margin: 2rem 0;
            }
            
            .status-pro h5 {
                color: #1d4ed8;
                margin-bottom: 0.5rem;
                font-weight: 600;
                display: flex;
                align-items: center;
            }
            
            .status-pro h5:before {
                content: '📁';
                margin-right: 0.5rem;
            }
        </style>
        """, unsafe_allow_html=True)

    def _run_async_in_thread(self, coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(coro)
        loop.close()
        return result

    def search_linkedin_jobs(self, keyword, location, limit, date_filter):
        if not keyword or not keyword.strip():
            st.error("❌ Lütfen bir anahtar kelime girin.")
            return

        with st.spinner(f"🔍 LinkedIn'de '{keyword}' pozisyonu aranıyor..."):
            try:
                date_mapping = {
                    "Son 24 saat": 1,
                    "Son 1 hafta": 7,
                    "Son 2 hafta": 14,
                    "Son 1 ay": 30,
                    "Hepsi": None
                }
                
                date_posted = date_mapping.get(date_filter)
                search_query = f"'{keyword}' pozisyonu için LinkedIn'de iş ilanı ara. Konum: {location}, Limit: {limit}"
                if date_posted:
                    search_query += f", Son {date_posted} gün"
                
                search_message = f"'{keyword}' pozisyonu için LinkedIn'de {limit} adet iş arama yap. Konum: {location}. Sonuçları Jobs/Job_Results/ klasörüne kaydet."
                result = self._run_async_in_thread(run_linkedin_agent(search_message))
                
                if result and result.get("success"):
                    json_files = list(self.job_results_path.glob("*.json"))
                    
                    if json_files:
                        latest_json = max(json_files, key=lambda x: x.stat().st_ctime)
                        result_msg = f"✅ **LinkedIn iş arama tamamlandı!**\n\n"
                        result_msg += f"🔍 **Aranan:** `{keyword}` - `{location}`\n"
                        result_msg += f"📊 **Limit:** {limit} ilan\n"
                        result_msg += f"📅 **Filtre:** {date_filter}\n"
                        result_msg += f"💾 Sonuçlar `Jobs/Job_Results/` klasörüne kaydedildi."
                        
                        st.success(result_msg)
                        st.info(f"📄 JSON dosyası: `{latest_json.name}`")
                    else:
                        st.warning("⚠️ Arama tamamlandı ancak sonuç dosyası bulunamadı.")
                        
                elif result and not result.get("success"):
                    st.error(f"❌ LinkedIn arama hatası: {result.get('error', 'Bilinmeyen hata')}")
                    
                else:
                    st.error("❌ LinkedIn arama işlemi başarısız oldu.")
                    
            except Exception as e:
                st.error(f"❌ Hata oluştu: {str(e)}")
                st.text_area("Hata detayları:", str(e), height=150)

    def create_tab(self):
        self._add_custom_css()
        
        st.markdown("""
        <div class="linkedin-hero">
            <div class="linkedin-hero-content">
                <h1>🔍 LinkedIn İş Arama</h1>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="search-form-pro">', unsafe_allow_html=True)
        st.markdown("### Arama Parametreleri")
        col1_1, col1_2 = st.columns(2)
        
        with col1_1:
            popular_positions = ["Seçiniz...", "Software Developer", "Data Scientist", "Frontend Developer", 
                               "Backend Developer", "DevOps Engineer", "Product Manager",
                               "UI/UX Designer", "Business Analyst", "QA Engineer"]
            
            previous_manual_keyword = st.session_state.get("linkedin_keyword_input", "").strip()
            
            if previous_manual_keyword:
                if previous_manual_keyword in popular_positions:
                    dropdown_index = popular_positions.index(previous_manual_keyword)
                else:
                    dropdown_index = 0
            else:
                dropdown_index = 0
            
            selected_position = st.selectbox(
                label="🎯 Anahtar Kelime / Pozisyon",
                options=popular_positions,
                index=dropdown_index,
                key="linkedin_position_selectbox",
                help="Popüler pozisyonlardan seçin"
            )
            
            if selected_position != "Seçiniz...":
                default_keyword = selected_position if not previous_manual_keyword else previous_manual_keyword
            else:
                default_keyword = previous_manual_keyword
            
            keyword_input = st.text_input(
                label="Veya manuel girin:",
                placeholder="Örn: Machine Learning Engineer, Python Developer",
                key="linkedin_keyword_input",
                value=default_keyword,
                help="Aranacak pozisyon veya beceri"
            )

        with col1_2:
            popular_cities = ["Seçiniz...", "İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Adana", "Türkiye"]
            
            previous_manual_location = st.session_state.get("linkedin_location_input", "").strip()
            
            if previous_manual_location:
                if previous_manual_location in popular_cities:
                    city_dropdown_index = popular_cities.index(previous_manual_location)
                else:
                    city_dropdown_index = 0  
            else:
                city_dropdown_index = 7 
            
            selected_city = st.selectbox(
                label="📍 Konum",
                options=popular_cities,
                index=city_dropdown_index,
                key="linkedin_city_selectbox", 
                help="Popüler şehirlerden seçin"
            )
            
            if selected_city != "Seçiniz...":
                default_location = selected_city if not previous_manual_location else previous_manual_location
            else:
                default_location = previous_manual_location
            
            location_input = st.text_input(
                label="Veya manuel girin:",
                placeholder="Örn: İstanbul, Ankara, Remote",
                key="linkedin_location_input",
                value=default_location,
                help="İş ilanlarının aranacağı konum"
            )
        
        col2_1, col2_2, col2_3 = st.columns(3)
        
        with col2_1:
            date_filter = st.selectbox(
                label="📅 Tarih Filtresi",
                options=["past week", "past month", "24hr"],
                index=0,
                key="linkedin_date_filter",
                help="İş ilanlarının yayınlanma tarihi"
            )
        
        with col2_2:
            job_type = st.selectbox(
                label="💼 İş Tipi",
                options=["", "full time", "part time", "contract", "temporary", "internship"],
                index=0,
                key="linkedin_job_type",
                help="İş türü (boş bırakılırsa tümü)"
            )
            
        with col2_3:
            limit_input = st.number_input(
                label="🔢 Maksimum Sonuç",
                min_value=5,
                max_value=50,
                step=1,
                value=10,
                key="linkedin_limit_input",
                help="Çekilecek maksimum iş ilanı sayısı"
            )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("🚀 İş Ara", type="primary", use_container_width=True):
                final_keyword = keyword_input.strip() if keyword_input.strip() else (selected_position if selected_position != "Seçiniz..." else "")
                final_location = location_input.strip() if location_input.strip() else (selected_city if selected_city != "Seçiniz..." else "Türkiye")
                
                if not final_keyword:
                    st.error("❌ Lütfen bir anahtar kelime girin.")
                else:
                    self.search_linkedin_jobs(final_keyword, final_location, limit_input, date_filter)

 