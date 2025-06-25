import os
import asyncio
import logging
import json
from pathlib import Path
from textwrap import dedent
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import Toolkit
from agno.tools.file import FileTools
from agno.utils.log import logger
from Tool.CoverLetterToolkit import CoverLetterToolkit
import dotenv
import sys
from typing import Optional
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

dotenv.load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def create_cover_letter_agent() -> Agent:
    cover_letter_toolkit = CoverLetterToolkit()
    file_toolkit = FileTools()
    
    instructions = dedent("""\
        Sen profesyonel bir ön yazı (cover letter) yazma uzmanısın. Görevin, bir adayın özgeçmişini 
        belirli bir iş ilanındaki gereksinimlere göre eşleştiren, kişiselleştirilmiş ve etkileyici 
        ön yazılar oluşturmak.
        
        İŞ AKIŞIN:
        1. ÖNCE get_job_details tool'unu kullanarak iş analizi dosyasını oku
        2. SONRA get_resume_analysis tool'unu kullanarak resume analizi dosyasını oku  
        3. Bu iki veriyi analiz ederek profesyonel bir cover letter oluştur
        
        KAPAK MEKTUBU OLUŞTURMA KURALLARI:
        
        1. **YAPISAL FORMAT**:
           - **Başlık ve Tarih**: Güncel tarih ve doğru format
           - **Profesyonel Selamlama**: "Sayın [Şirket Adı] İnsan Kaynakları Ekibi"
           - **Güçlü Giriş**: Pozisyon ve ilgi beyanı (1 paragraf)
           - **Ana Paragraflar**: Deneyim-pozisyon uyumu vurgulama (2-3 paragraf)
           - **Güçlü Kapanış**: Görüşme talebi ve teşekkür (1 paragraf)
           - **Profesyonel İmza**: Ad soyad ve iletişim bilgileri
        
        2. **İÇERİK STRATEJİSİ**:
           - İş pozisyonuna özel ilgi ve motivasyon göster
           - CV'deki en güçlü 2-3 deneyimi pozisyonla ilişkilendir
           - Teknik becerileri iş gereksinimleriyle eşleştir
           - Başarıları sayısal verilerle destekle (%70 doğruluk, 200 çalışan vb.)
           - Şirkete sağlayacağı değer ve gelecek katkıları vurgula
           - Öğrenme ve gelişim motivasyonunu belirt
        
        3. **TON ve STIL**:
           - Profesyonel ama samimi ve sıcak bir dil kullan
           - 300-500 kelime arası tut, çok uzun olmasın
           - Klişelerden kaçın, spesifik ve sonuç odaklı ol
           - Mükemmel dilbilgisi ve yazım kurallarına dikkat et
           - Türkçe yaz
        
        4. **ÖRNEK YAPISAL ŞABLON**:
        
        25 Haziran 2025
        
        Sayın [Şirket Adı] İnsan Kaynakları Ekibi,
        
        [İş unvanı] pozisyonu için başvurumu sunmaktan büyük memnuniyet duyuyorum. [Şirket hakkında kısa pozitif yorum ve neden bu şirkette çalışmak istediği].
        
        [CV'deki en güçlü deneyimi ile pozisyon arasında bağlantı kurma]. [Teknik becerilerini ve başarılarını sayısal verilerle vurgulama]. [Bu deneyimlerin hedeflenen pozisyonda nasıl avantaj sağlayacağını açıklama].
        
        [İkinci güçlü deneyim veya beceri alanı]. [Şirkete katkı sağlayacağı konular]. [Öğrenme ve gelişim konusundaki istekliliği].
        
        Deneyimlerimi ve becerilerimi [şirket adı]'nda değerlendirme fırsatı bulmak için bir görüşme talep ediyorum. İlginiz ve zamanınız için teşekkür ederim.
        
        Saygılarımla,
        [Ad Soyad]
        [E-posta]
        [Telefon]
        
        5. **KİŞİSELLEŞTİRME KURALLARI**:
           - Kişisel bilgileri CV analizinden çek ve kullan
           - İş bilgilerini job analizinden al ve doğru kullan
           - CV'deki güçlü yönleri pozisyonla eşleştir
           - Spesifik başarı örnekleri ver (proje sonuçları, iyileştirmeler)
           - Şirket değerleri veya misyonuna uyumlu ifadeler kullan
        
        ÖNEMLI: 
        - Dosyaları okuyamazsan veya hata alırsan, detaylı hata mesajı ver
        - Her adımda tool çağrısı yap, manuel işlem yapma
        - Sadece cover letter metnini döndür, başka açıklama yazma
        - Format tam olarak yukarıdaki şablona uygun olmalı
        - Son çıktı kullanıma hazır, minimal düzenleme gerektiren kalitede olmalı
        - TÜM ÇIKTILARINI VE KAPAK MEKTUPLARİNİ TÜRKÇE OLARAK VER
    """)
    
    return Agent(
        model=OpenAIChat(id="gpt-4o"),
        tools=[cover_letter_toolkit, file_toolkit],
        instructions=instructions,
        markdown=True,
        show_tool_calls=True,
    )

async def run_agent(job_data_path: str, resume_data_path: str, max_jobs: int = 3, output_path: Optional[str] = None) -> dict:
    try:
        logger.info(f"Cover letter ajanı başlatılıyor...")
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        else:
            os.makedirs("Jobs/Cover_Letters", exist_ok=True)
        
        agent = await create_cover_letter_agent()
        with open(job_data_path, 'r', encoding='utf-8') as f:
            job_data = json.load(f)
        
        if isinstance(job_data, dict) and "results" in job_data:
            raw_jobs = job_data["results"][:max_jobs]
            jobs = []
            for i, job_item in enumerate(raw_jobs):
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
            jobs = job_data[:max_jobs]
        elif isinstance(job_data, dict) and "result" in job_data:
            jobs = job_data["result"][:max_jobs]
        elif isinstance(job_data, dict):
            job_items = list(job_data.items())[:max_jobs]
            jobs = []
            for job_title, job_details in job_items:
                if " - " in job_title:
                    position, company = job_title.split(" - ", 1)
                else:
                    position = job_title
                    company = job_details.get("company_information", "Bilinmeyen Şirket")
                    if company == "Belirtilmemiş":
                        company = "Bilinmeyen Şirket"
                
                job_obj = {
                    "position": position,
                    "company": company,
                    "analysis": job_details
                }
                jobs.append(job_obj)
        else:
            jobs = list(job_data.values())[:max_jobs] if job_data else []
        
        logger.info(f"Toplam {len(jobs)} iş için cover letter oluşturulacak")
        
        cover_letters = {}
        for i, job in enumerate(jobs):
            try:
                company_name = job.get("company", f"Şirket_{i+1}")
                position = job.get("position", f"Pozisyon_{i+1}")
                
                if "analysis" in job:
                    analysis = job.get("analysis", {})
                    if analysis:
                        company_info = analysis.get("company_information", "")
                        if company_info and company_info != "Belirtilmemiş":
                            company_name = company_info.split(",")[0].split(".")[0].strip() or company_name
                        
                        position_details = analysis.get("position_details", "")
                        if position_details and position_details != "Belirtilmemiş":
                            position = position_details.split(",")[0].strip() or position
                
                def safe_ascii_encode(text):
                    if isinstance(text, str):
                        return text.encode('ascii', errors='replace').decode('ascii')
                    return str(text)
                
                safe_company = safe_ascii_encode(company_name)
                safe_position = safe_ascii_encode(position)
                
                from datetime import datetime
                ay_cevirileri = {
                    "January": "Ocak", "February": "Şubat", "March": "Mart", 
                    "April": "Nisan", "May": "Mayıs", "June": "Haziran",
                    "July": "Temmuz", "August": "Ağustos", "September": "Eylül", 
                    "October": "Ekim", "November": "Kasım", "December": "Aralık"
                }
                tarih_obj = datetime.now()
                gun = tarih_obj.strftime("%d").lstrip("0")
                ay_en = tarih_obj.strftime("%B")
                yil = tarih_obj.strftime("%Y")
                ay_tr = ay_cevirileri.get(ay_en, ay_en)
                current_date = f"{gun} {ay_tr} {yil}"
                
                message = f"""
                Create a professional cover letter:
                
                JOB INFORMATION:
                Company: {safe_company}
                Position: {safe_position}
                
                JOB DETAILS:
                {json.dumps(job, ensure_ascii=True, indent=2)}
                
                CV ANALYSIS FILE: {resume_data_path}
                
                INSTRUCTIONS:
                1. Use get_resume_analysis tool to read CV data
                2. Compare job requirements with CV analysis
                3. Create a high-quality cover letter in Turkish with this format:
                
                REQUIRED FORMAT:
                {current_date}
                
                Sayin {safe_company} Insan Kaynaklari Ekibi,
                
                {safe_position} pozisyonu icin basvurumu sunmaktan buyuk memnuniyet duyuyorum. [Company hakkinda olumlu yorum ve bu sirkette calisma motivasyonu].
                
                [CV'deki en guclu deneyim alanini pozisyonla iliskilendirme]. [Teknik beceriler ve sayisal basari verileri]. [Bu deneyimin hedef pozisyonda saglayacagi avantajlar].
                
                [Ikinci guclu yon ve sirkete katki potansiyeli]. [Ogrenme ve gelisim istekliligi].
                
                Deneyimlerimi ve becerilerimi {safe_company}'da degerlendirme firsati bulmak icin bir gorusme talep ediyorum. Ilginiz ve zamaniniz icin tesekkur ederim.
                
                Saygilarimla,
                [CV'den alinan ad soyad]
                [CV'den alinan e-posta]
                [CV'den alinan telefon]
                
                CRITICAL POINTS:
                - Use personal info from CV (name, email, phone)
                - Highlight technical skills matching the position
                - Add numerical achievement data if available
                - Keep between 300-500 words
                - Return ONLY the letter text, nothing else
                - Write in proper Turkish with correct characters (use ğ, ü, ş, ı, ö, ç)
                """
                
                result = await agent.arun(message)
                if hasattr(result, 'content'):
                    cover_letter = result.content
                elif hasattr(result, 'response'):
                    cover_letter = result.response
                else:
                    cover_letter = str(result)
                
                job_file = Path(job_data_path).stem
                resume_file = Path(resume_data_path).stem
                safe_company_filename = company_name.replace(" ", "_").replace("/", "_").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ı", "i").replace("ö", "o").replace("ç", "c")
                safe_position_filename = position.replace(" ", "_").replace("/", "_").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ı", "i").replace("ö", "o").replace("ç", "c")
                
                output_file = f"Jobs/Cover_Letters/cover_letter_{safe_company_filename}_{safe_position_filename}_{job_file}_{resume_file}.txt"
                
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(cover_letter)
                
                cover_letters[f"{company_name} - {position}"] = {
                    "content": cover_letter,
                    "file_path": output_file,
                    "company": company_name,
                    "position": position
                }
                
                logger.info(f"Cover letter oluşturuldu: {company_name} - {position}")
                
            except Exception as e:
                logger.error(f"İş {i+1} için cover letter hatası: {e}")
                cover_letters[f"Hata_{i+1}"] = {
                    "content": f"Bu iş için cover letter oluşturulamadı: {str(e)}",
                    "file_path": "",
                    "company": f"Hata_{i+1}",
                    "position": "Hata"
                }
        
        logger.info(f"Toplam {len(cover_letters)} cover letter oluşturuldu")
        return {
            "success": True,
            "message": f"Toplam {len(cover_letters)} cover letter oluşturuldu",
            "cover_letters": cover_letters,
            "total_jobs": len(jobs),
            "processed_jobs": len(cover_letters)
        }
                
    except Exception as e:
        logger.error(f"Ajan çalıştırma hatası: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": f"Cover letter oluşturma hatası: {str(e)}",
            "cover_letters": {},
            "total_jobs": 0,
            "processed_jobs": 0
        }

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        job_data_path = sys.argv[1]
        resume_data_path = sys.argv[2]
        max_jobs = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        output_path = sys.argv[4] if len(sys.argv) > 4 else None
        
        asyncio.run(run_agent(job_data_path, resume_data_path, max_jobs, output_path))
    else:
        print("Kullanım: python cover_letter_agent_all.py <iş_analiz_dosya_yolu> <özgeçmiş_analiz_dosya_yolu> <max_iş_sayısı> [çıktı_dosya_yolu]")