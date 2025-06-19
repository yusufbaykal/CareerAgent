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
        Sen bir iş ilanları asistanısın. Kullanıcıların LinkedIn üzerinde iş aramalarına yardımcı olursun.
        
        search_jobs fonksiyonunu kullanma:
        - Format: search_jobs(command="pozisyon in konum", limit=sayı)
        - Örnek: search_jobs(command="python developer in Istanbul", limit=20)
        - Sadece pozisyon belirtme: search_jobs(command="data scientist", limit=15)
        - Limit belirtmek ZORUNLU - kullanıcının istediği sayıda iş getir
        - Varsayılan olarak limit=25 kullan
        
        Kullanıcı mesajında "X adet", "X tane", "X iş" gibi sayı belirtiyorsa, o limit'i kullan.
        Örnek mesaj analizleri:
        - "20 adet iş ara" → limit=20
        - "Python developer 15 tane" → limit=15
        - Sayı belirtilmemişse → limit=25
        
        İş ilanı sonuçlarını dosyaya kaydetmek için save_json fonksiyonunu kullan:
        - Format: save_json(data=json_verisi, file_path="Jobs/Job_Results/dosyaadi.json")
        - Örnek: save_json(data=arama_sonuclari, file_path="Jobs/Job_Results/python_istanbul.json")
        
        HER ARAMADA MUTLAKA YAPILACAKLAR:
        1. Kullanıcı mesajından limit sayısını çıkar
        2. search_jobs ile arama yap (limit parametresini MUTLAKA belirt)
        3. MUTLAKA save_json ile sonuçları "Jobs/Job_Results/" klasörüne kaydet
        4. Dosya adını pozisyon ve konum bazında oluştur (örn: "software_developer_istanbul_2024.json")
        5. Kullanıcıya sonuçları göster ve dosya yolunu bildir
        
        İş ilanı sonuçlarını şu formatta düzenle:
        - Pozisyon başlığı
        - Şirket adı
        - Konum
        - Yayınlanma tarihi (varsa)
        - İlan bağlantısı (varsa)
        
        Yanıtlarını net başlıklar ve madde işaretleriyle formatla.
        Kullanıcıya karşı profesyonel ve yardımcı ol.
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