import asyncio
import logging
from textwrap import dedent
from urllib.parse import urlparse
from pathlib import Path
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.utils.log import logger
import dotenv
dotenv.load_dotenv()
from Tool.DocumentParserToolkit import DocumentParserToolkit
from Tool.WebScraperToolkit import WebScraperToolkit
from Tool.JobAnalysisToolkit import JobAnalysisToolkit
from Tool.FileToolkit import FileToolkit    
import sys
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def generate_filename_from_url(url: str) -> str:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.split('.')[0]
    path_parts = [p for p in parsed_url.path.split('/') if p]
    position_keywords = ["developer", "engineer", "manager", "analyst", "specialist", "assistant"]
    position = ""
    for part in path_parts:
        for keyword in position_keywords:
            if keyword in part.lower():
                position = part
                break
        if position:
            break                
    if not position and path_parts:
        position = path_parts[-1]
    
    position = re.sub(r'[^a-zA-Z0-9]', '_', position)
    filename = f"{domain}_{position}"
    
    return filename

async def create_job_analysis_agent() -> Agent:
    doc_parser = DocumentParserToolkit()
    web_scraper = WebScraperToolkit()
    job_analyzer = JobAnalysisToolkit()
    file_toolkit = FileToolkit()
    
    instructions = dedent("""\
        Sen bir iş ilanı analiz uzmanısın. Kullanıcılara farklı kaynaklardan gelen iş ilanlarını
        anlamlandırmalarına ve analiz etmelerine yardımcı olursun.
        
        🚨 KRİTİK UYARI: SADECE JSON FORMATINDA KAYDET! TXT FORMATINDA ASLA KAYDETME! 🚨
        
        ## İŞ İLANI ANALİZ ADIMLARI:
        
        1. **İLAN KAYNAĞI BELİRLE:**
           - Dosya: parse_document() kullan
           - URL: fetch_url_content() veya fetch_linkedin_job() kullan
           - LinkedIn Arama: search_linkedin_jobs() kullan
        
        2. **İLANI ANALİZ ET:**
           - analyze_job_description() ile detaylı analiz yap
           - extract_job_details() ile yapılandırılmış formata dönüştür
        
        3. **SONUÇLARI JSON OLARAK KAYDET:**
           - save_json(data=ANALIZ_SONUÇLARI, file_path="dosya.json") kullan
           - MUTLAKA .json uzantısı ile kaydet
        
        ## GEREKLİ JSON YAPISI:
        ```json
        {
          "summary": "Pozisyon özeti",
          "company_information": "Şirket bilgisi", 
          "mission_vision": "Misyon ve vizyon",
          "position_details": "Pozisyon detayları",
          "experience_level": "Junior/Mid-level/Senior",
          "work_environment": "Uzaktan/Hibrit/Ofis", 
          "years_of_experience": "X+ yıl",
          "tech_stack": ["teknoloji1", "teknoloji2"],
          "requirements": ["gereksinim1", "gereksinim2"],
          "responsibilities": ["sorumluluk1", "sorumluluk2"],
          "nice_to_have": ["isteğe_bağlı1", "isteğe_bağlı2"],
          "benefits": ["avantaj1", "avantaj2"],
          "culture_hints": ["kültür_ipucu1", "kültür_ipucu2"],
          "motivation_points": ["motivasyon_noktası1", "motivasyon_noktası2"]
        }
        ```
        
        ## ANALİZ EDİLECEK BİLGİLER:
        - Pozisyon başlığı ve seviyesi (Junior/Mid-level/Senior)
        - Şirket bilgileri, misyon/vizyon
        - Çalışma ortamı (Uzaktan/Hibrit/Ofis)
        - Deneyim gereksinimleri
        - Teknik beceriler (tech_stack)
        - Gereksinimler ve sorumluluklar
        - İsteğe bağlı beceriler (nice_to_have)
        - Avantajlar ve şirket kültürü ipuçları
        - Motivasyon noktaları
        
        ## KAYDETME KURALLARI:
        - ❌ save_text() YASAK!
        - ❌ .txt dosyası YASAK!
        - ✅ save_json() ZORUNLU!
        - ✅ .json uzantısı ZORUNLU!
        - ✅ Yukarıdaki JSON yapısına UYGUN olmalı!
        
        Analiz sonuçlarını temiz, düzenli ve yapılandırılmış bir formatta sunmaya özen göster.
    """)
    
    return Agent(
        model=OpenAIChat(
            id="gpt-4o",
        ),
        tools=[doc_parser, web_scraper, job_analyzer, file_toolkit],
        instructions=instructions,
        markdown=True,
        show_tool_calls=True,
    )


async def run_agent(message: str) -> str:
    try:
        url_match = re.search(r'https?://[^\s]+', message)
        if url_match:
            url = url_match.group(0)            
            filename = generate_filename_from_url(url)
            project_root = Path(__file__).parent.parent
            output_dir = project_root / "Jobs" / "Job_Analysis"
            output_dir.mkdir(parents=True, exist_ok=True)
            file_path = output_dir / f"{filename}.json"
            if "dosyasına kaydet" not in message:
                message = f"{message} ve sonuçları {file_path} dosyasına kaydet."
        
        logger.info(f"Job Analysis Agent başlatılıyor, sorgu: '{message}'")
        
        agent = await create_job_analysis_agent()
        
        result = await agent.arun(message)
        
        return result
                
    except Exception as e:
        logger.error(f"Agent çalıştırma hatası: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return f"❌ Hata: {str(e)}"


if __name__ == "__main__":
    message = sys.argv[1] if len(sys.argv) > 1 else "https://hubx.breezy.hr/p/100f78632ca7-backend-developer adresindeki iş ilanını analiz et"
    
    asyncio.run(run_agent(message))