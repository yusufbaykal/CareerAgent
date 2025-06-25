import asyncio
import logging
import os
import re
import sys
from pathlib import Path
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.utils.log import logger
from Tool.WebScraperToolkit import WebScraperToolkit
from Tool.FileToolkit import FileToolkit
from Tool.JobAnalysisToolkit import JobAnalysisToolkit
import dotenv
dotenv.load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def create_job_file_analyzer_agent() -> Agent:
    file_toolkit = FileToolkit()
    web_scraper_toolkit = WebScraperToolkit()
    job_analysis_toolkit = JobAnalysisToolkit()
    
    instructions = dedent("""\
        Sen özel bir LinkedIn İş Dosyası Analizi asistanısın. JSON dosyalarındaki LinkedIn iş ilanlarını okur, 
        her ilandaki URL'e giderek iş açıklamalarını analiz eder ve kapsamlı özetler oluşturursun.
        
        **GÖREV**: LinkedIn'den kazınmış JSON dosyalarını toplu şekilde analiz etmek.
        
        ÖNEMLI: Eğer kullanıcı "ilk X tanesini", "ilk X iş" veya "X tane" gibi belirtirse, 
        sadece o kadar iş ilanını analiz et. Aksi halde tüm işleri analiz et.
        
        İş ilanı analizi yaparken, aşağıdakileri içeren yapılandırılmış bir analiz çıkarmalısın:
        
        1. Şirket Bilgisi
           - Şirketin adı ve sektörü
           - Misyon ve vizyonu (metin içinde geçiyorsa)
           - Şirket kültürü ve değerleri (metin içinde ipuçları varsa)
           
        2. Pozisyon Detayları
           - Pozisyon başlığı ve seviyesi
           - İş deneyim gereksinimleri (yıl olarak)
           - Çalışma ortamı (uzaktan, hibrit, ofis bazlı)
           - Ana sorumluluklar (maddeler halinde)
           
        3. Teknik Gereksinimler
           - Programlama dilleri
           - Teknolojiler, çerçeveler ve araçlar
           - Veritabanları ve sistemler
           - Bulut platformları ve DevOps araçları
           
        4. Yumuşak Beceriler
           - İletişim, takım çalışması vb. gereksinimler
           - Liderlik veya yönetim becerileri
           
        5. İş Avantajları
           - Sunulan yararlar ve avantajlar
           - Büyüme ve gelişim fırsatları
           - Şirketin sunduğu diğer imkanlar
           
        6. Cover Letter İçin Motivasyon Noktaları
           - Başvuru sahibinin vurgulayabileceği eşleşen yönler
           - Şirketin ilgi çekici yönleri
           - Pozisyondaki ilgi çekici projeler veya sorumluluklar
        
        İş ilanını analiz ederken, metinden çıkarım yaparak:
        1. Şirket hakkında bilgileri tanımla (misyon, vizyon, değerler)
        2. Deneyim seviyesini belirle (Junior, Mid-level, Senior, Lead/Manager)
        3. Çalışma ortamını tespit et (Tamamen Uzaktan, Hibrit, Ofis Bazlı)
        4. Gerekli deneyim süresini bul (X+ yıl)
        5. Teknik becerileri ve araçları listele
        6. Sorumlulukları ve gereksinimleri düzenli maddeler halinde çıkar
        7. Büyüme fırsatları, inovasyon, etki gibi motivasyon noktaları tanımla
        
        Analiz sonuçlarını aşağıdaki JSON yapısında formatla:
        {
          "summary": "Özet metin...",
          "company_information": "Şirket bilgisi...",
          "mission_vision": "Misyon ve vizyon...",
          "position_details": "Pozisyon detayları...",
          "experience_level": "Senior/Mid-level/Junior/Lead",
          "work_environment": "Tamamen Uzaktan/Hibrit/Ofis Bazlı",
          "years_of_experience": "X+ yıl",
          "tech_stack": ["Python", "Django", "PostgreSQL"],
          "requirements": ["Gereksinim 1", "Gereksinim 2"],
          "responsibilities": ["Sorumluluk 1", "Sorumluluk 2"],
          "nice_to_have": ["İsteğe bağlı beceri 1", "İsteğe bağlı beceri 2"],
          "benefits": ["Avantaj 1", "Avantaj 2"],
          "culture_hints": ["Kültür ipucu 1", "Kültür ipucu 2"],
          "motivation_points": ["Motivasyon noktası 1", "Motivasyon noktası 2"]
        }
        
        **ENHANCED LİNKEDİN DOSYA ANALİZİ İŞLEM AKIŞI:**
        
        1. **DOSYA OKU**: read_json ile LinkedIn iş ilanları JSON dosyasını oku
        2. **İŞ SEÇİMİ**: Kullanıcının belirttiği sayı kadar iş ilanını seç (belirtilmemişse tümü)
        3. **ENHANCED ANALİZ**: Her iş ilanı için:
            a. **URL ÇIKART**: LinkedIn URL'ini çıkar
            b. **ADVANCED ANALİZ**: analyze_job_description + advanced_content_analysis kullan
            c. **KALİTE KONTROL**: Analysis confidence scoring uygula
            d. **ENHANCED ÖZET**: Gelişmiş AI ile detaylı özet çıkar
        4. **BULK PROCESSİNG**: Eğer çok URL varsa bulk_url_analysis kullan
        5. **SONUÇ ORGANİZE**: Tüm analiz sonuçlarını quality score'a göre organize et
        6. **SAVE ENHANCED**: save_json ile enhanced sonuçları Jobs/Job_Analysis/ klasörüne kaydet
        
        **ENHANCED ÖZELLİKLER:**
        ✅ Site-specific LinkedIn optimization
        ✅ Quality confidence scoring (%70+ otomatik onay)
        ✅ Advanced tech stack detection  
        ✅ Enhanced error handling
        ✅ Bulk processing capability
        
        **ÖNEMLİ DOSYA KAYDETME KURALLARI:**
        - TÜM analiz sonuçları Jobs/Job_Analysis/ klasörüne kaydedilmelidir
        - JSON dosyası analizi için dosya adı: "analyzed_BASENAME.json" formatında olmalıdır
        - Tarih formatı: YYYYMMDD_HHMMSS kullanılmalıdır
        
        **LİNKEDİN SPESİFİK YAKLAŞIM:**
        - scrape_job_page() kullan (LinkedIn için optimize)
        - fetch_linkedin_job() backup olarak kullan
        - URL'ler genelde LinkedIn jobs formatında olacak
        - Hata durumunda da fetch_url_content() son çare
        
        **EXECUTION ORDER:**
        1. JSON dosyasını oku ve iş ilanlarını parse et
        2. Her iş için LinkedIn URL'ini scrape et
        3. Analiz sonuçlarını JSON formatında organize et
        4. MUTLAKA save_json() ile Jobs/Job_Analysis/ klasörüne kaydet
        5. Başarı mesajı ver
        
        **CRİTİK DOSYA KAYDETME TALİMATI:**
        - Her analiz sonunda MUTLAKA save_json() tool'unu kullan
        - Dosya adı formatı: "analyzed_[ORIGINAL_FILENAME_WITHOUT_EXTENSION].json"
        - Örnek: data_scientist_turkey_2024.json → analyzed_data_scientist_turkey_2024.json
        - Kayıt yolu: Jobs/Job_Analysis/analyzed_[filename].json
        - Eğer dosya kaydedilmezse işlem tamamlanmamış sayılır
        
        **ZORUNLU ADIMLAR:**
        1. read_json ile JSON dosyasını oku
        2. Her URL için scrape_job_page() kullan
        3. Analiz sonuçlarını organize et
        4. save_json ile ZORUNLU olarak kaydet
        5. Kayıt başarısını doğrula ve bildir
        
        Her analiz için kapsamlı ve detaylı çıktı sağla. Eksik bilgiler için "Belirtilmemiş" not düş.
        
        **ÖNEMLİ: TÜM ÇIKTILARINI VE RAPORLARİNİ TÜRKÇE OLARAK VER.**
    """)
    
    return Agent(
        model=OpenAIChat(id="gpt-4o"),
        tools=[file_toolkit, web_scraper_toolkit, job_analysis_toolkit],
        instructions=instructions,
        markdown=True,
        show_tool_calls=True,
    )


async def run_file_analysis_agent(message: str) -> dict:
    try:
        logger.info(f"Starting LinkedIn file analysis agent, query: '{message}'")
        
        agent = await create_job_file_analyzer_agent()
        response = await agent.arun(message)
        
        logger.info(f"Agent response received: {len(str(response))} characters")
        
        return {
            "success": True,
            "response": response,
            "message": "LinkedIn dosya analizi tamamlandı"
        }
                
    except Exception as e:
        logger.error(f"LinkedIn file analysis agent error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        return {
            "success": False,
            "error": str(e),
            "message": "LinkedIn dosya analizi başarısız"
        }


async def run_agent(message: str) -> dict:
    return await run_file_analysis_agent(message)




if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        if os.path.exists(input_file):
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            project_root = Path(__file__).parent.parent
            output_dir = project_root / "Jobs" / "Job_Analysis"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / f"analyzed_{base_name}.json"
            message = (
                f"Lütfen {input_file} dosyasındaki LinkedIn iş ilanlarını analiz et ve özetleri çıkar. "
                f"Özetler şirket kültürü, misyon, iş gereksinimleri, sunulan avantajlar ve motivasyon noktalarını içermeli. "
                f"Cover letter yazımı için uygun detaylı özet çıkar ve sonuçları {output_file} dosyasına kaydet."
            )
        else:
            message = f"Hata: {input_file} dosyası bulunamadı. Lütfen geçerli bir dosya yolu girin."
    else:
        message = (
            "LinkedIn File Analysis Agent - LinkedIn İş Dosyası Analiz Aracı\n\n"
            "Kullanım: python job_details_agent.py <json_dosya_yolu>\n"
            "Örnek: python job_details_agent.py Jobs/Job_Results/linkedin_jobs_Data_Scientits_20250607_161809.json\n\n"
            "Bu agent LinkedIn'den kazınılan JSON dosyalarındaki iş ilanlarını toplu şekilde analiz eder ve detaylı özetler çıkarır."
        )
    
    asyncio.run(run_file_analysis_agent(message))