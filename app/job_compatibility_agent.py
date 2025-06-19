import asyncio
import logging
from textwrap import dedent
from pathlib import Path

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.utils.log import logger

from Tool.JobCompatibilityToolkit import JobCompatibilityToolkit
from Tool.FileToolkit import FileToolkit
import dotenv
dotenv.load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def create_job_compatibility_agent() -> Agent:
    compatibility_toolkit = JobCompatibilityToolkit()
    file_toolkit = FileToolkit()
    
    instructions = dedent("""\
        Sen bir İş Uygunluğu Analiz Uzmanısın. Görevin, iş ilanı analizi ile CV analizi arasında 
        karşılaştırma yaparak adayın işe uygunluğunu 10 üzerinden skorlamaktır.
        
        ÖNEMLI: Eğer kullanıcı "X. iş ilanını", "belirli bir iş" veya spesifik bir iş indeksi belirtirse,
        sadece o işi analiz et. Aksi halde tüm işleri analiz et.
        
        İŞ AKIŞI:
        1. load_job_analysis ile iş analizi dosyasını yükle
           Format: load_job_analysis(job_analysis_file="analyzed_job_file.json")
        2. load_resume_analysis ile CV analizi dosyasını yükle  
           Format: load_resume_analysis(resume_analysis_file="resume_analysis.json")
        3. Eğer spesifik iş belirtilmişse, sadece o işi seç
        4. analyze_compatibility ile uygunluk analizini yap
           Format: analyze_compatibility(job_data=job_verileri, resume_data=cv_verileri)
        5. save_compatibility_report ile raporu kaydet
           Format: save_compatibility_report(compatibility_report=rapor, job_title="pozisyon", candidate_name="aday_adi")
        
        SKORLAMA KRİTERLERİ (10 üzerinden):
        - **Teknik Beceriler (25%)**: İş ilanındaki teknik gereksinimler ile CV'deki beceriler uyumu
        - **Deneyim Seviyesi (25%)**: İşin gerektirdiği deneyim ile adayın deneyimi uyumu
        - **Eğitim Geçmişi (15%)**: İş için gerekli eğitim seviyesi uyumu
        - **Sektör Deneyimi (15%)**: İlgili sektörde çalışma deneyimi
        - **Dil Yeterlilikleri (10%)**: İş için gerekli dil becerileri
        - **Ek Beceriler (10%)**: Sertifikalar, kurslar, özel yetenekler
        
        ÇIKTI FORMATI:
        - Genel Uygunluk Skoru: X/10
        - Teknik Beceri Skoru: X/10  
        - Deneyim Skoru: X/10
        - Eğitim Skoru: X/10
        - Güçlü Yönler: [liste]
        - Gelişim Alanları: [liste]
        - Adaya Öneriler: [liste]
        - Detaylı Analiz Raporu
        
        TEK İŞ ANALİZİ:
        Spesifik bir iş analiz edilirken:
        - Hangi işin analiz edildiğini belirt (şirket - pozisyon)
        - O işin spesifik gereksinimlerine odaklan
        - CV ile o işin özel uyumunu değerlendir
        - Rapor dosya adına iş bilgisini ekle
        
        ÖRNEKLER:
        - 8-10 puan: Mükemmel uyum, kesinlikle başvurmalı
        - 6-7 puan: İyi uyum, başvuruda bulunabilir  
        - 4-5 puan: Orta uyum, eksiklikleri giderip başvurabilir
        - 1-3 puan: Düşük uyum, bu pozisyon için uygun değil
        
        Her analiz sonrasında net ve objektif değerlendirme yap.
        Analiz başlamadan önce hangi iş(ler)in analiz edileceğini belirt.
    """)
    
    return Agent(
        name="Is_Uygunluk_Test_Uzmani",
        role="is_ilani_cv_uygunluk_analizi_ve_skorlama",
        model=OpenAIChat(id="gpt-4o"),
        tools=[compatibility_toolkit, file_toolkit],
        instructions=instructions,
        show_tool_calls=True,
        markdown=True,
    )


async def run_agent(message: str) -> None:
    try:
        logger.info(f"İş uygunluğu test agent'ı başlatılıyor: '{message}'")
        
        agent = await create_job_compatibility_agent()
        
        await agent.aprint_response(message, stream=True)
                
    except Exception as e:
        logger.error(f"İş uygunluğu agent hatası: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 2:
        job_analysis_file = sys.argv[1]  
        resume_analysis_file = sys.argv[2]
        
        message = (
            f"Lütfen {job_analysis_file} iş analizi dosyası ile {resume_analysis_file} CV analizi dosyasını "
            f"karşılaştırarak uygunluk analizi yap. Adayın işe uygunluğunu 10 üzerinden skorla ve "
            f"detaylı rapor oluştur."
        )
    else:
        message = (
            "İş Uygunluğu Test Agent'ı - İş İlanı ve CV Karşılaştırma Aracı\n\n"
            "Kullanım: python job_compatibility_agent.py <is_analizi.json> <cv_analizi.json>\n"
            "Örnek: python job_compatibility_agent.py analyzed_job.json resume_analysis.json\n\n"
            "Bu agent iş ilanı analizi ile CV analizini karşılaştırır ve 10 üzerinden uygunluk skoru verir."
        )
    
    asyncio.run(run_agent(message)) 