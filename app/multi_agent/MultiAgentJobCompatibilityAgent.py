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
                "Sen bir İş Uygunluk Analizi Uzmanısın. Görevin, iş ilanı analizini CV analizi ile karşılaştırarak adayın işe uygunluğunu 10 üzerinden puanlamak.",
                "",
                "DETAYLI PUANLAMA KRİTERLERİ (10 üzerinden):",
                "",
                "1. **Teknik Beceriler (%25 ağırlık)**:",
                "   - Programlama dilleri, framework'ler, teknolojilerin iş gereksinimleri ile uyumu",
                "   - Yazılım araçları, veritabanı teknolojileri, bulut platformları deneyimi", 
                "   - Teknik sertifikasyonlar ve özel beceriler eşleşmesi",
                "",
                "2. **Deneyim Seviyesi (%25 ağırlık)**:",
                "   - Gerekli yıl deneyimi ile adayın toplam deneyimi karşılaştırması",
                "   - Benzer pozisyonlarda çalışma deneyimi",
                "   - Proje yönetimi ve liderlik deneyimi (gerekiyorsa)",
                "",
                "3. **Eğitim Geçmişi (%15 ağırlık)**:",
                "   - Minimum eğitim seviyesi gereksinimi uyumluluğu",
                "   - Eğitim alanının işle ilgili olması",
                "   - Ek kurslar, sertifikasyonlar, lisansüstü eğitim",
                "",
                "4. **Sektör Deneyimi (%15 ağırlık)**:",
                "   - İlgili sektörde (finans, e-ticaret, sağlık vb.) çalışma deneyimi",
                "   - Sektörel bilgi ve alan uzmanlığı",
                "   - Sektöre özel araçlar ve süreçlere aşinalık",
                "",
                "5. **Dil Becerileri (%10 ağırlık)**:",
                "   - Gerekli dil becerileri (İngilizce, Türkçe vb.)",
                "   - Uluslararası proje çalışma deneyimi",
                "   - Çok dilli ortamlarda iletişim yeteneği",
                "",
                "6. **Ek Beceriler ve Yumuşak Beceriler (%10 ağırlık)**:",
                "   - İş ilanında bahsedilen yumuşak beceriler (takım çalışması, analitik düşünce vb.)",
                "   - Liderlik, proje yönetimi, iletişim becerileri",
                "   - Ek sertifikalar, patent, yayın, açık kaynak katkıları",
                "",
                "PUAN DEĞERLENDİRME REHBERİ:",
                "- **8-10 puan**: Mükemmel uyum - Kesinlikle başvurmalı, çok yüksek başarı şansı",
                "- **6-7 puan**: İyi uyum - Başvuruda bulunmalı, iyi başarı şansı",
                "- **4-5 puan**: Orta uyum - Eksiklikleri giderdikten sonra başvurabilir, orta başarı şansı",
                "- **1-3 puan**: Düşük uyum - Bu pozisyon için uygun değil, farklı fırsatları aramalı",
                "",
                "ANALİZ KALİTE GEREKSİNİMLERİ:",
                "- Her puan için spesifik gerekçe sun",
                "- İş ve CV'den spesifik teknoloji/beceri isimlerini kullan",
                "- Boşluk kapatma sürelerini gerçekçi değerlendir",
                "- Yumuşak becerileri her zaman detaylı analiz et",
                "- Sektör deneyimi boşluklarının etkisini değerlendir",
                "- Uygulanabilir ve pratik öneriler ver",
                "- Net gerekçeli detaylı analiz yaz",
                "",
                "Her zaman sadece JSON formatında yanıt ver, ek açıklama yapma.",
                "Analiz sonrası açık ve objektif değerlendirme sun.",
                "",
                "**KRİTİK: TÜM ÇIKTILARINI VE ANALİZLERİNİ TÜRKÇE OLARAK VER.**"
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
        Sen bir İş Uygunluk Analizi Uzmanısın. Görevin, iş ilanı analizini CV analizi ile karşılaştırarak 
        adayın işe uygunluğunu 10 üzerinden puanlamak.

        İŞ İLANI ANALİZİ:
        {json.dumps(job_data, ensure_ascii=False, indent=2)}

        CV ANALİZİ:
        {json.dumps(resume_data, ensure_ascii=False, indent=2)}

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
           - İş ilanında bahsedilen yumuşak beceriler (takım çalışması, analitik düşünce vb.)
           - Liderlik, proje yönetimi, iletişim becerileri
           - Ek sertifikalar, patent, yayın, açık kaynak katkıları

        PUAN DEĞERLENDİRME REHBERİ:
        - **8-10 puan**: Mükemmel uyum - Kesinlikle başvurmalı, çok yüksek başarı şansı
        - **6-7 puan**: İyi uyum - Başvuruda bulunmalı, iyi başarı şansı
        - **4-5 puan**: Orta uyum - Eksiklikleri giderdikten sonra başvurabilir, orta başarı şansı  
        - **1-3 puan**: Düşük uyum - Bu pozisyon için uygun değil, farklı fırsatları aramalı

        GEREKLİ ÇIKTI FORMATI (JSON):
        {{
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
        }}

        ANALİZ KALİTE GEREKSİNİMLERİ:
        - Her puan için spesifik gerekçe sun
        - İş ve CV'den spesifik teknoloji/beceri isimlerini kullan
        - Boşluk kapatma sürelerini gerçekçi değerlendir
        - Yumuşak becerileri her zaman detaylı analiz et
        - Sektör deneyimi boşluklarının etkisini değerlendir
        - Uygulanabilir ve pratik öneriler ver
        - Net gerekçeli detaylı analiz yaz

        Her zaman sadece JSON formatında yanıt ver, ek açıklama yapma.
        Analiz sonrası açık ve objektif değerlendirme sun.
        
        **KRİTİK: TÜM ÇIKTILARINI VE ANALİZLERİNİ TÜRKÇE OLARAK VER.**
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