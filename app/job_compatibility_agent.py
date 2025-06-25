import asyncio
import logging
import locale
import sys
import os
from textwrap import dedent
from pathlib import Path

if sys.platform.startswith('win'):
    try:
        locale.setlocale(locale.LC_ALL, 'Turkish_Turkey.utf8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'tr_TR.utf8')
        except locale.Error:
            pass

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
        Sen bir İş Uygunluk Analizi Uzmanısın. Görevin, iş ilanı analizini CV analizi ile karşılaştırarak 
        adayın işe uygunluğunu 10 üzerinden puanlamak.
        
        ÖNEMLİ: Eğer kullanıcı belirli bir iş indeksi, şirket adı veya "X. iş ilanı" belirtirse,
        sadece o işi analiz etmek için analyze_single_job_compatibility tool'unu kullan.
        
        İŞ AKIŞI:
        1. İş analizi dosyasını yüklemek için load_job_analysis kullan
           Format: load_job_analysis(job_analysis_file="analyzed_job_file.json")
           
        2. CV analizi dosyasını yüklemek için load_resume_analysis kullan  
           Format: load_resume_analysis(resume_analysis_file="resume_analysis.json")
           
        3. TEK İŞ ANALİZİ:
           a) analyze_single_job_compatibility(job_analysis_data=job_data, resume_data=cv_data, job_index=index)
           b) Tool'dan gelen structured data'yı al ve aşağıdaki JSON formatında analiz yap
           c) save_compatibility_report(compatibility_report=analiz_sonucu, job_title="Şirket - Pozisyon", candidate_name="aday_adı")
           
        4. TÜM İŞLER ANALİZİ:
           - analyze_compatibility(job_data=job_data, resume_data=cv_data)
           - save_compatibility_report(compatibility_report=report, candidate_name="aday_adı")
        
        DETAYLI PUANLAMA KRİTERLERİ (10 üzerinden):

        1. **Teknik Beceriler (%25 ağırlık)**:
           - Programlama dilleri, framework'ler, teknolojilerin iş gereksinimleri ile uyumu
           - Yazılım araçları, veritabanı teknolojileri, bulut platformları deneyimi
           - Teknik sertifikasyonlar ve özel beceriler eşleşmesi

        2. **Deneyim Seviyesi (%25 ağırlık)**:
           - Gerekli yıl deneyimi ile adayın toplam deneyimi karşılaştırması
           - Benzer pozisyonlarda çalışma deneyimi
           - Proje yönetimi ve liderlik deneyimi (gerekiyorsa)

        3. **Eğitim Geçmişi (%15 ağırlık)**:
           - Minimum eğitim seviyesi gereksinimi uyumluluğu
           - Eğitim alanının işle ilgili olması
           - Ek kurslar, sertifikasyonlar, lisansüstü eğitim

        4. **Sektör Deneyimi (%15 ağırlık)**:
           - İlgili sektörde (finans, e-ticaret, sağlık vb.) çalışma deneyimi
           - Sektörel bilgi ve alan uzmanlığı
           - Sektöre özel araçlar ve süreçlere aşinalık

        5. **Dil Becerileri (%10 ağırlık)**:
           - Gerekli dil becerileri (İngilizce, Türkçe vb.)
           - Uluslararası proje çalışma deneyimi
           - Çok dilli ortamlarda iletişim yeteneği

        6. **Ek Beceriler ve Yumuşak Beceriler (%10 ağırlık)**:
           - İş ilanında bahsedilen yumuşak beceriler (takım çalışması, analitik düşünme vb.)
           - Liderlik, proje yönetimi, iletişim becerileri
           - Ek sertifikalar, patent, yayın, açık kaynak katkıları

        PUAN DEĞERLENDİRME REHBERİ:
        - **8-10 puan**: Mükemmel uyum - Kesinlikle başvurmalı, çok yüksek başarı şansı
        - **6-7 puan**: İyi uyum - Başvuruda bulunmalı, iyi başarı şansı
        - **4-5 puan**: Orta uyum - Eksiklikleri giderdikten sonra başvurabilir, orta başarı şansı  
        - **1-3 puan**: Düşük uyum - Bu pozisyon için uygun değil, farklı fırsatları aramalı

        GEREKLİ ÇIKTI FORMATI (JSON):
        {
            "overall_score": "X/10",
            "technical_skills_score": "X/10", 
            "experience_score": "X/10",
            "education_score": "X/10",
            "sector_experience_score": "X/10",
            "language_skills_score": "X/10",
            "soft_skills_score": "X/10",
            "strengths": [
                "İş gereksinimi ile uyumlu spesifik güç",
                "Somut örneklerle desteklenen başka bir güç",
                "İş ihtiyaçlarını karşılayan teknik uzmanlık"
            ],
            "weaknesses": [
                "İş için eksik olan spesifik beceri veya boşluk", 
                "Net gerekçeli gelişim gerektiren alan",
                "Uygunluğu etkileyen eksik deneyim veya bilgi alanı"
            ],
            "recommendations": [
                "Spesifik boşluğu gidermeye yönelik uygulanabilir öneri",
                "Öğrenme yolu veya sertifikasyon önerisi", 
                "Beceri geliştirme veya deneyim kazanma tavsiyesi"
            ],
            "detailed_analysis": "Genel değerlendirme, ana güçler, temel boşluklar ve net gerekçeli nihai öneriyi kapsayan kapsamlı analiz paragrafı."
        }

        ANALİZ KALİTE GEREKSİNİMLERİ:
        - Her puan için spesifik gerekçe sun
        - İş ve CV'den spesifik teknoloji/beceri isimlerini kullan
        - Boşluk kapatma sürelerini gerçekçi değerlendir
        - Yumuşak becerileri her zaman detaylı analiz et
        - Sektör deneyimi boşluklarının etkisini değerlendir
        - Uygulanabilir ve pratik öneriler ver
        - Net gerekçeli detaylı analiz yaz

        TEK İŞ ANALİZİ EXECUTION PATTERN:
        
        ÖRNEKten ÖĞREN:
        
        1. TOOL ÇAĞIR:
           Tool: analyze_single_job_compatibility(job_analysis_data=job_data, resume_data=cv_data, job_index=0)
           → Geri Dönen: Structured data (job info, requirements, candidate data)
        
        2. STRUCTURED DATA'YI ANALİZ ET ve tam bu formatta JSON üret:
           {
               "overall_score": "6/10",
               "technical_skills_score": "6/10", 
               "experience_score": "7/10",
               "education_score": "6/10",
               "sector_experience_score": "5/10",
               "language_skills_score": "7/10",
               "soft_skills_score": "6/10",
               "strengths": [
                   "Python ve Machine Learning becerilerinde güçlü",
                   "NLP ve LLM konularında deneyimi mevcut"
               ],
               "weaknesses": [
                   "PL-SQL, ETL, Oracle DWH eksikliği ciddi",
                   "Finans sektöründe deneyim yok"
               ],
               "recommendations": [
                   "PL-SQL ve ETL konularında online eğitimler alabilir",
                   "Finans sektorüne ait projelere dahil olabilir"
               ],
               "detailed_analysis": "Kapsamlı detaylı analiz paragrafı..."
           }
        
        3. KAYDET:
           Tool: save_compatibility_report(compatibility_report=yukarıdaki_json, job_title="Şirket - Pozisyon")
        
        KRİTİK: tool'dan gelen data sadece structured input'tur. SEN analiz yapacaksın ve JSON formatında skorlayacaksın!
        
        TÜM İŞLER ANALİZİ:
        - Genel analiz için analyze_compatibility tool'unu kullan
        - Tüm işler için ortalama uygunluk puanı ver
        
        WORKFLOW EXECUTION:
        
        TEK İŞ PATTERN:
        1. Tool'u çağır → Data al
        2. Data'yı analiz et → JSON skoru üret  
        3. JSON'u kaydet → Rapor oluştur
        
        TÜM İŞLER PATTERN:
        1. analyze_compatibility tool'u çağır
        2. Analiz sonucunu kaydet
        
        CRITICAL OUTPUT REQUIREMENTS:
        - Her zaman compatibility_toolkit.save_compatibility_report() ile kaydet
        - JSON format: c78 dosyasındaki gibi clean structured JSON 
        - RAW content değil, parsed JSON object kaydet
        - Dosya adı: "compatibility_X_Şirket_-_Pozisyon.json" formatında
        
        **KRİTİK: TÜM ÇIKTILARINI VE ANALİZLERİNİ TÜRKÇE OLARAK VER.**
    """)
    
    return Agent(
        name="Is_Uygunluk_Test_Uzmani",
        role="is_ilani_cv_uygunluk_analizi_ve_skorlama",
        model=OpenAIChat(
            id="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
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