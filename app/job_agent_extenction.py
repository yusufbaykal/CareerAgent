import asyncio
import logging
from textwrap import dedent


from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.utils.log import logger

from Tool.FileToolkit import FileToolkit
from Tool.LinkedInJobsToolkit import LinkedInJobsToolkit
import dotenv
dotenv.load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def create_agent() -> Agent:
    linkedin_toolkit = LinkedInJobsToolkit()
    
    file_toolkit = FileToolkit()
    
    instructions = dedent("""\
        Sen bir LinkedIn İş Arama asistanısın. Kullanıcının istediklerini anlayıp LinkedIn'de iş ara ve sonuçları dosyaya kaydet.
        
        ## GÖREVLER:
        1. **Input Parsing**: Kullanıcı mesajından pozisyon, konum ve sayı çıkar
        2. **Arama**: search_jobs ile LinkedIn'de ara
        3. **Dosya Kaydet**: save_json ile Jobs/Job_Results/ klasörüne kaydet
        4. **Bilgi Ver**: Kaç ilan bulundu ve nereye kaydedildi bildir
        
        ## ARAMA PARAMETRELERİ:
        - **Format**: "pozisyon in konum" 
        - **Limit**: Kullanıcı "X adet" derse X, belirtmezse 25
        - **Dosya Adı**: pozisyon_konum_tarih.json formatında
        
        ## ÖRNEKLER:
        - "Python developer in Istanbul" → search_jobs(command="Python developer in Istanbul", limit=25)
        - "50 adet Data Scientist" → limit=50 kullan
        
        **MUTLAKA yapman gerekenler:**
        1. search_jobs() çağır
        2. save_json() ile kaydet
        3. Türkçe sonuç bildir
    """)
    
    return Agent(
        model=OpenAIChat(
            id="gpt-4o",
        ),
        tools=[linkedin_toolkit, file_toolkit],
        instructions=instructions,
        markdown=True,
        show_tool_calls=True,
        
    )


async def run_agent(message: str) -> dict:
    try:
        logger.info(f"Agent başlatılıyor, sorgu: '{message}'")
        
        agent = await create_agent()
        
        response = await agent.arun(message)
        logger.info(f"Agent yanıtı alındı: {len(str(response))} karakter")
        
        return {
            "success": True,
            "response": response,
            "message": "LinkedIn arama tamamlandı"
        }
                
    except Exception as e:
        logger.error(f"Agent çalıştırma hatası: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        return {
            "success": False,
            "error": str(e),
            "message": "LinkedIn arama başarısız"
        }


if __name__ == "__main__":
    asyncio.run(run_agent("Türkiye'de Senior Python Developer pozisyonları bul ve sonuçları job_results/senior_python_turkey.json dosyasına kaydet"))