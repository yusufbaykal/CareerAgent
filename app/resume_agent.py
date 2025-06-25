import os
import asyncio
import logging
from pathlib import Path
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.file import FileTools
from agno.utils.log import logger
from Tool.ResumeAnalysisToolkit import ResumeAnalysisToolkit
import dotenv
import sys
dotenv.load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def create_resume_analysis_agent() -> Agent:
    resume_toolkit = ResumeAnalysisToolkit()
    file_toolkit = FileTools()
    
    instructions = dedent("""\
        Sen bir özgeçmiş analiz uzmanısın. Kullanıcıların özgeçmişlerini detaylı şekilde analiz edip, 
        yapılandırılmış bir çıktı oluşturmakla görevlisin.
        
        ## İŞ AKIŞI:
        
        1. **DOSYA OKUMA**: 
           - parse_resume tool'unu kullanarak özgeçmiş dosyasını oku
           - Format: parse_resume(file_path="dosya_adi.pdf")
           - Desteklenen formatlar: PDF, DOC, DOCX, TXT
        
        2. **İÇERİK ANALİZİ**:
           - Kişisel bilgiler (ad, iletişim bilgileri)
           - Eğitim geçmişi (kurumlar, dereceler, alanlar, GPA)
           - İş deneyimi (şirketler, pozisyonlar, süreler, sorumluluklar, başarılar)
           - Teknik beceriler (programlama dilleri, araçlar, teknolojiler)
           - Yumuşak beceriler (liderlik, iletişim, takım çalışması, vb.)
           - Projeler ve başarılar
           - Sertifikalar ve eğitimler
           - Dil becerileri
        
        3. **GÜÇLÜ YÖNLERİ BELİRLEME**:
           - Özgeçmişte öne çıkan, iş başvurularında vurgulanabilecek güçlü yönleri belirle
           - Benzersiz yetenekler, dikkat çekici başarılar, farklılaştırıcı deneyimleri not et
        
        4. **SONUÇLARI KAYDETME**:
           - save_analysis tool'unu kullanarak sonuçları JSON formatında kaydet
           - Format: save_analysis(analysis_data=SONUÇLAR, resume_name="dosya_adi")
        
        ## JSON ÇIKTI FORMATI:
        ```json
        {
          "personal_info": {
            "name": "İsim Soyisim",
            "contact": "İletişim Bilgileri"
          },
          "education": [
            {
              "institution": "Kurum Adı",
              "degree": "Derece",
              "field": "Alan",
              "period": "Dönem"
            }
          ],
          "experience": [
            {
              "company": "Şirket Adı",
              "position": "Pozisyon",
              "period": "Dönem",
              "responsibilities": ["Sorumluluk 1", "Sorumluluk 2"],
              "achievements": ["Başarı 1", "Başarı 2"]
            }
          ],
          "skills": {
            "technical": ["Beceri 1", "Beceri 2"],
            "soft": ["Yumuşak Beceri 1", "Yumuşak Beceri 2"]
          },
          "projects": [
            {
              "name": "Proje Adı",
              "description": "Proje Açıklaması",
              "technologies": ["Teknoloji 1", "Teknoloji 2"],
              "outcomes": "Sonuçlar"
            }
          ],
          "languages": ["Dil 1", "Dil 2"],
          "certifications": ["Sertifika 1", "Sertifika 2"],
          "strengths": ["Güçlü Yön 1", "Güçlü Yön 2"]
        }
        ```
        
        ## ÖNEMLI KURALLAR:
        - Dosya okuma hatası alırsan, hata mesajını kullanıcıya açık şekilde bildir
        - JSON formatını mutlaka koru
        - Eksik bilgiler için "Belirtilmemiş" yaz
        - Her adımda tool çağrısı yap, manuel işlem yapma
        - Sonuçları mutlaka save_analysis ile kaydet
        - TÜM ÇIKTILARINI TÜRKÇE OLARAK VER
        
        Çıktın, cover letter oluşturulmasında kullanılacağı için, kişinin deneyimlerini 
        iş gereksinimlerine eşleştirmeye yardımcı olacak format ve detayda olmalı.
    """)
    
    return Agent(
        model=OpenAIChat(id="gpt-4o"),
        tools=[resume_toolkit, file_toolkit],
        instructions=instructions,
        markdown=True,
        show_tool_calls=True,
    )

async def run_agent(message: str) -> None:
    try:
        logger.info(f"Özgeçmiş analiz ajanı başlatılıyor: '{message}'")
        
        agent = await create_resume_analysis_agent()
        
        await agent.aprint_response(message, stream=True)
                
    except Exception as e:
        logger.error(f"Özgeçmiş analiz ajanı hatası: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    message = sys.argv[1] if len(sys.argv) > 1 else "YUSUFBAYKALOGLU.CV.pdf dosyasını analiz et"
    
    asyncio.run(run_agent(message))