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
        
        Cover letter oluştururken şu yönergeleri takip et:
        
        1. YAPI:
           - Profesyonel bir selamlama ve giriş (1 paragraf)
           - İlgili deneyim ve becerileri vurgulayan ana metin (2-3 paragraf)
           - Güçlü bir sonuç ve eylem çağrısı (1 paragraf)
           - Profesyonel bir kapanış
        
        2. İÇERİK STRATEJİSİ:
           - Özel pozisyona ve şirkete ilgi gösteren etkileyici bir giriş ile başla
           - Özgeçmişten iş gereksinimlerini doğrudan karşılayan 3-5 kilit niteliği vurgula
           - Gerekli becerileri gösteren spesifik başarı örnekleri sun
           - Şirketin misyonunu, değerlerini veya sektör zorluklarını anladığını göster
           - Şirkete katkıda bulunma fırsatı için heyecan göster
           - Sonraki adımlar için net bir eylem çağrısıyla bitir
        
        3. STIL KURALLARI:
           - Ön yazıyı kısa ve öz tut (250-400 kelime)
           - Profesyonel ama samimi bir dil kullan
           - Klişelerden ve genel ifadelerden kaçın
           - Spesifik ve sonuç odaklı ol
           - Şirket kültürüne uygun bir ton kullan (resmi/geleneksel vs. rahat/startup)
           - Mükemmel dilbilgisi ve yazım kurallarına dikkat et
        
        ÖNEMLI: Dosyaları okuyamazsan veya herhangi bir hata ile karşılaşırsan, 
        detaylı bir hata mesajı ver ve sorunu açıkla.
        
        Son cover letter, minimal düzenleme gerektiren, kullanıma hazır bir şekilde olmalıdır.
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
            jobs = job_data["results"][:max_jobs]
        elif isinstance(job_data, list):
            jobs = job_data[:max_jobs]
        elif isinstance(job_data, dict) and "result" in job_data:
            jobs = job_data["result"][:max_jobs]
        else:
            jobs = list(job_data.values())[0][:max_jobs] if job_data else []
        
        logger.info(f"Toplam {len(jobs)} iş için cover letter oluşturulacak")
        
        cover_letters = {}
        for i, job in enumerate(jobs):
            try:
                if "analysis" in job:
                    company_name = job.get("company", f"Şirket_{i+1}")
                    position = job.get("position", f"Pozisyon_{i+1}")
                    analysis = job.get("analysis", {})
                    if analysis:
                        company_info = analysis.get("company_information", "")
                        if company_info and company_info != "Belirtilmemiş":
                            company_name = company_info.split(",")[0].split(".")[0].strip() or company_name
                        
                        position_details = analysis.get("position_details", "")
                        if position_details and position_details != "Belirtilmemiş":
                            position = position_details
                else:
                    company_name = job.get("company", f"Şirket_{i+1}")
                    position = job.get("position", f"Pozisyon_{i+1}")
                
                message = f"""
                Lütfen aşağıdaki bilgileri kullanarak profesyonel bir cover letter oluştur:
                
                İŞ BİLGİLERİ:
                Şirket: {company_name}
                Pozisyon: {position}
                
                Bu tek iş için detaylı bilgiler:
                {json.dumps(job, ensure_ascii=False, indent=2)}
                
                Resume analizi dosyası: {resume_data_path}
                
                Lütfen get_resume_analysis tool'unu kullanarak resume verilerini oku ve 
                bu spesifik iş için kişiselleştirilmiş bir cover letter oluştur.
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
                safe_company = company_name.replace(" ", "_").replace("/", "_")
                safe_position = position.replace(" ", "_").replace("/", "_")
                
                output_file = f"Jobs/Cover_Letters/cover_letter_{safe_company}_{safe_position}_{job_file}_{resume_file}.txt"
                
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