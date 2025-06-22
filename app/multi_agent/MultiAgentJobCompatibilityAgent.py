import json
from pathlib import Path
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools

class MultiAgentJobCompatibilityAgent(Agent):
    def __init__(self, workflow_id: str = None, **kwargs):
        super().__init__(
            name="Multi-Agent Job Compatibility Agent",
            role="İş ilanı analizi ile CV analizi arasında detaylı karşılaştırma yaparak adayın işe uygunluğunu kapsamlı bir şekilde değerlendirir ve profesyonel rapor oluşturur.",
            model=OpenAIChat(id="gpt-4o"),
            tools=[
                ReasoningTools(add_instructions=True)
            ],
            instructions=[
                "İş ilanı ve CV analizlerini çok detaylı karşılaştır.",
                "6 farklı kategoride değerlendirme yap (teknik, deneyim, eğitim, sektör, dil, ek beceriler).",
                "10 üzerinden skorla ve her skor için net gerekçe sun.",
                "Güçlü yönleri ve eksiklikleri spesifik olarak belirt.",
                "Adaya pratik ve uygulanabilir öneriler ver.",
                "JSON formatında profesyonel rapor oluştur."
            ],
            **kwargs
        )
        self.workflow_id = workflow_id

    def load_job_analysis(self) -> dict:
        try:
            job_file_path = Path(f"Jobs/Job_Analysis/{self.workflow_id}_single_job_analysis.json")
            if job_file_path.exists():
                with open(job_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"İş analizi dosyası bulunamadı: {job_file_path}")
                return {}
        except Exception as e:
            print(f"İş analizi dosyası okuma hatası: {e}")
            return {}

    def load_resume_analysis(self) -> dict:
        try:
            resume_file_path = Path(f"Jobs/Resume_Analysis/{self.workflow_id}_resume_analysis.json")
            if resume_file_path.exists():
                with open(resume_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"CV analizi dosyası bulunamadı: {resume_file_path}")
                return {}
        except Exception as e:
            print(f"CV analizi dosyası okuma hatası: {e}")
            return {}

    def analyze_and_save_compatibility(self) -> str:
        if not self.workflow_id:
            return "Hata: Workflow ID belirlenmemiş."

        print("İş ve CV analizleri yükleniyor...")
        job_data = self.load_job_analysis()
        resume_data = self.load_resume_analysis()

        if not job_data:
            return "Hata: İş analizi dosyası bulunamadı veya okunamadı."
        if not resume_data:
            return "Hata: CV analizi dosyası bulunamadı veya okunamadı."

        compatibility_prompt = f"""
        Sen bir İş Uygunluğu Analiz Uzmanısın. Aşağıdaki iş ilanı analizi ve CV analizini kapsamlı bir şekilde karşılaştırarak adayın işe uygunluğunu değerlendir.

        İŞ İLANI ANALİZİ:
        {json.dumps(job_data, ensure_ascii=False, indent=2)}

        CV ANALİZİ:
        {json.dumps(resume_data, ensure_ascii=False, indent=2)}

        DETAYLI SKORLAMA KRİTERLERİ (10 üzerinden):

        1. **Teknik Beceriler (25% ağırlık)**:
           - İş ilanındaki programlama dilleri, frameworkler, teknolojiler ile CV'deki beceriler uyumu
           - Yazılım araçları, database teknolojileri, cloud platformları deneyimi
           - Teknik sertifikasyonlar ve özel beceriler uyumu

        2. **Deneyim Seviyesi (25% ağırlık)**:
           - İşin gerektirdiği yıl deneyimi ile adayın toplam deneyimi karşılaştırması
           - Benzer pozisyonlarda çalışma deneyimi
           - Proje yönetimi ve liderlik deneyimi (gerekiyorsa)

        3. **Eğitim Geçmişi (15% ağırlık)**:
           - İş için gerekli minimum eğitim seviyesi uyumu
           - Eğitim alanının işle ilgili olması
           - Ek kurslar, sertifikasyonlar, lisansüstü eğitim

        4. **Sektör Deneyimi (15% ağırlık)**:
           - İlgili sektörde (finans, e-ticaret, healthcare vb.) çalışma deneyimi
           - Sektörel bilgi ve domain expertise
           - Sektöre özel araçlar ve süreçlere aşinalık

        5. **Dil Yeterlilikleri (10% ağırlık)**:
           - İş için gerekli dil becerileri (İngilizce, Türkçe vb.)
           - Uluslararası projelerde çalışma deneyimi
           - Çok dilli ortamlarda iletişim yeteneği

        6. **Ek Beceriler ve Soft Skills (10% ağırlık)**:
           - İş ilanında bahsedilen soft skillsler (takım çalışması, analitik düşünme vb.)
           - Liderlik, proje yönetimi, iletişim becerileri
           - Ek sertifikalar, patent, yayın, açık kaynak katkıları

        PUAN DEĞERLENDİRME REHBERİ:
        - **8-10 puan**: Mükemmel uyum - Kesinlikle başvurmalı, çok yüksek başarı şansı
        - **6-7 puan**: İyi uyum - Başvuruda bulunmalı, iyi başarı şansı var
        - **4-5 puan**: Orta uyum - Eksiklikleri giderip başvurabilir, orta başarı şansı  
        - **1-3 puan**: Düşük uyum - Bu pozisyon için uygun değil, farklı fırsatlara yönelmeli

        LÜTFEN AŞAĞIDAKİ JSON FORMATINI AYNEN KULLAN:
        {{
            "overall_score": "8/10",
            "technical_skills_score": "7/10", 
            "experience_score": "9/10",
            "education_score": "8/10",
            "sector_experience_score": "6/10",
            "language_skills_score": "8/10",
            "soft_skills_score": "7/10",
            "strengths": [
                "İş ilanında aranan Python ve Machine Learning becerisine güçlü şekilde sahip",
                "NLP ve LLM konularında 3+ yıl deneyimi mevcut",
                "Mikroservis mimarisi ve cloud teknolojileri tecrübesi değerli",
                "İngilizce iletişim becerileri iş gereksinimleriyle uyumlu"
            ],
            "weaknesses": [
                "İş ilanında belirtilen SQL Server ve Azure deneyimi sınırlı görünüyor", 
                "Finans sektörü deneyimi eksik, domain knowledge geliştirmeli",
                "Soft skills değerlendirmesi CV'de yeterince belirtilmemiş",
                "Proje yönetimi sertifikası bulunmuyor"
            ],
            "recommendations": [
                "SQL Server ve Azure konularında Microsoft sertifikasyonu alabilir",
                "Finans domain'inde online kurslar ve projeler yapabilir", 
                "LinkedIn profilinde soft skills ve başarı hikayelerini vurgulayabilir",
                "PMP veya Agile sertifikasyonu için başvuruda bulunabilir",
                "GitHub'da daha fazla açık kaynak projeye katkıda bulunabilir"
            ],
            "detailed_analysis": "Aday, pozisyon için genel olarak çok güçlü bir profil sergilemektedir. Özellikle teknik beceriler alanında Machine Learning ve NLP deneyimi, iş gereksinimlerinin %80'ini karşılamaktadır. 5 yıllık yazılım geliştirme deneyimi, pozisyonun deneyim gereksinimlerini aşmaktadır. Mikroservis mimarisi ve Python uzmanlığı büyük artılar. Ancak finans sektöründe domain bilgisi ve SQL Server konusunda gelişim alanları bulunmaktadır. Bu eksikliklerin kısa sürede kapatılabileceği değerlendirilmektedir. Soft skills açısından takım çalışması deneyimi mevcut ancak liderlik deneyimi sınırlıdır. Genel değerlendirme olarak aday işe başvurmalı ve yüksek başarı şansına sahiptir."
        }}

        ÖNEMLİ NOTLAR:
        - Her skor için net gerekçe belirt
        - Spesifik teknoloji/beceri isimlerini kullan  
        - Eksiklikleri kapatma süresini değerlendir
        - Soft skills analizi mutlaka yap
        - Sektör deneyimi eksikliğini dikkate al
        - Uygulanabilir öneriler ver

        Sadece JSON formatında yanıt ver, başka açıklama ekleme.
        """

        try:
            print("LLM ile detaylı uygunluk analizi yapılıyor...")
            response = self.run(compatibility_prompt)
            
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            if "```json" in response_content:
                response_content = response_content.split("```json")[1].split("```")[0].strip()
            elif "```" in response_content:
                response_content = response_content.split("```")[1].split("```")[0].strip()
            
            compatibility_data = json.loads(response_content)
            
            output_dir = Path(f"Jobs/Job_Compatibility/")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file_path = output_dir / f"compatibility_{self.workflow_id}.json"

            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(compatibility_data, f, ensure_ascii=False, indent=4)

            print(f"Detaylı uygunluk raporu kaydedildi: {output_file_path}")
            return f"Uygunluk analizi başarıyla tamamlandı ve '{output_file_path}' konumuna kaydedildi."
            
        except json.JSONDecodeError as e:
            print(f"JSON ayrıştırma hatası: {e}")
            print(f"LLM yanıtı: {response_content[:500]}...")
            
            return self.create_template_compatibility_report()
            
        except Exception as e:
            print(f"Uygunluk analizi sırasında beklenmeyen hata: {e}")
            return f"Hata: Uygunluk analizi yapılamadı. Detaylar: {e}"

    def create_template_compatibility_report(self) -> str:
        template_data = {
            "overall_score": "5/10",
            "technical_skills_score": "5/10",
            "experience_score": "5/10", 
            "education_score": "5/10",
            "sector_experience_score": "3/10",
            "language_skills_score": "5/10",
            "soft_skills_score": "3/10",
            "strengths": [
                "Otomatik analiz yapılamadığı için manuel değerlendirme gerekiyor",
                "CV ve iş ilanı verileri yüklendi ancak karşılaştırma tamamlanamadı"
            ],
            "weaknesses": [
                "İş ve CV verileri tam olarak karşılaştırılamadı",
                "Otomatik skorlama sistemi çalışmadı",
                "Detaylı analiz için manuel inceleme gerekli"
            ],
            "recommendations": [
                "CV formatını kontrol edin ve eksik bilgileri tamamlayın",
                "İş ilanı detaylarının doğru çekildiğinden emin olun",
                "Teknik beceriler listesini güncelleyin",
                "Deneyim bölümünde spesifik teknolojileri belirtin",
                "Soft skills ve başarı hikayelerini CV'ye ekleyin"
            ],
            "detailed_analysis": "Otomatik uygunluk analizi sistem hatası nedeniyle tamamlanamadı. Bu template rapor, sistem sorununu göstermektedir. Gerçek analiz için iş ilanı ve CV verilerinin doğru formatta yüklendiğinden ve LLM'nin erişebildiğinden emin olunmalıdır. Manual değerlendirme yapılması önerilir.",
            "note": "Bu bir template raporudur. Gerçek analiz için geçerli veri ve çalışan sistem gereklidir.",
            "system_error": "LLM uygunluk analizi başarısız oldu"
        }
        
        output_dir = Path(f"Jobs/Job_Compatibility/")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file_path = output_dir / f"compatibility_{self.workflow_id}.json"

        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, ensure_ascii=False, indent=4)

        print(f"Template uygunluk raporu kaydedildi: {output_file_path}")
        return f"Uygunluk analizi otomatik yapılamadı, detaylı template rapor '{output_file_path}' konumuna kaydedildi." 