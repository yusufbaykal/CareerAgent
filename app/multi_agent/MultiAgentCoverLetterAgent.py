import json
from pathlib import Path
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools

class MultiAgentCoverLetterAgent(Agent):
    def __init__(self, workflow_id: str = None, **kwargs):
        super().__init__(
            name="Multi-Agent Cover Letter Agent",
            role="İş ilanı analizi, CV analizi ve uygunluk raporunu kullanarak kişiselleştirilmiş bir ön yazı (cover letter) oluşturur.",
            model=OpenAIChat(id="gpt-4o"),
            tools=[
                ReasoningTools(add_instructions=True)
            ],
            instructions=[
                "İş ilanı, CV ve uygunluk analizlerini birleştir.",
                "Kişiselleştirilmiş ve etkileyici bir kapak mektubu yaz.",
                "Adayın güçlü yanlarını vurgula ve pozisyonla uyumunu göster.",
                "Profesyonel ve samimi bir ton kullan."
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

    def load_compatibility_report(self) -> dict:
        try:
            compatibility_file_path = Path(f"Jobs/Job_Compatibility/compatibility_{self.workflow_id}.json")
            if compatibility_file_path.exists():
                with open(compatibility_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Uygunluk raporu dosyası bulunamadı: {compatibility_file_path}")
                return {}
        except Exception as e:
            print(f"Uygunluk raporu dosyası okuma hatası: {e}")
            return {}

    def generate_and_save_cover_letter(self) -> str:
        if not self.workflow_id:
            return "Hata: Workflow ID belirlenmemiş."

        print("İş, CV ve uygunluk analizleri yükleniyor...")
        job_data = self.load_job_analysis()
        resume_data = self.load_resume_analysis()
        compatibility_data = self.load_compatibility_report()

        if not job_data:
            return "Hata: İş analizi dosyası bulunamadı veya okunamadı."
        if not resume_data:
            return "Hata: CV analizi dosyası bulunamadı veya okunamadı."
        if not compatibility_data:
            return "Hata: Uygunluk raporu dosyası bulunamadı veya okunamadı."

        cover_letter_prompt = f"""
        Aşağıdaki bilgileri kullanarak profesyonel ve kişiselleştirilmiş bir kapak mektubu yaz:

        İŞ İLANI ANALİZİ:
        {json.dumps(job_data, ensure_ascii=False, indent=2)}

        CV ANALİZİ:
        {json.dumps(resume_data, ensure_ascii=False, indent=2)}

        UYGUNLUK RAPORU:
        {json.dumps(compatibility_data, ensure_ascii=False, indent=2)}

        KAPAK MEKTUBU KURALLARI:
        1. **Başlık ve Tarih**: Güncel tarih ve doğru format
        2. **Profesyonel Selamlama**: "Sayın İnsan Kaynakları Ekibi" veya şirket özel
        3. **Güçlü Giriş**: Pozisyon ve ilgi beyanı
        4. **Ana Paragraflar**: Deneyim-pozisyon uyumu vurgulama
        5. **Güçlü Kapanış**: Görüşme talebi ve teşekkür
        6. **Profesyonel İmza**: Ad soyad ve iletişim

        ÖRNEK YAPISAL FORMAT:
        
        [Tarih]
        
        Sayın [Şirket Adı] İnsan Kaynakları Ekibi,
        
        [İş unvanı] pozisyonu için başvurumu sunmaktan büyük memnuniyet duyuyorum. [Şirket hakkında kısa yorum ve neden çalışmak istediği].
        
        [CV'deki en güçlü 2-3 deneyimi pozisyonla ilişkilendirme]. [Teknik becerilerini vurgulama]. [Başarılarını sayısal verilerle destekleme].
        
        [Şirkete sağlayacağı değer ve gelecek katkıları]. [Öğrenme ve gelişim motivasyonu].
        
        Deneyimlerimi ve becerilerimi [şirket adı]'nda değerlendirme fırsatı bulmak için bir görüşme talep ediyorum. İlginiz ve zamanınız için teşekkür ederim.
        
        Saygılarımla,
        [Ad Soyad]
        [E-posta]
        [Telefon]

        ÖNEMLİ TALİMATLAR:
        - Kişisel bilgileri CV'den al: {resume_data.get('personal_info', {}).get('name', 'İsim bulunamadı')}
        - İş bilgilerini job analizinden al: {job_data.get('job_title', 'Pozisyon bulunamadı')} - {job_data.get('company_name', 'Şirket bulunamadı')}
        - Uygunluk raporundaki güçlü yönleri vurgula
        - Teknik becerileri pozisyonla eşleştir
        - Samimi ama profesyonel ton kullan
        - 300-500 kelime arası tut
        - Türkçe yaz

        Sadece kapak mektubu metnini döndür, başka hiçbir şey yazma.
        """

        try:
            print("LLM ile kapak mektubu oluşturuluyor...")
            response = self.run(cover_letter_prompt)
            
            cover_letter_content = response.content if hasattr(response, 'content') else str(response)
            
            output_dir = Path(f"Jobs/Cover_Letters/")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file_path = output_dir / f"{self.workflow_id}_cover_letter.txt"

            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(cover_letter_content)

            print(f"Kapak mektubu kaydedildi: {output_file_path}")
            return f"Kapak mektubu başarıyla oluşturuldu ve '{output_file_path}' konumuna kaydedildi."
            
        except Exception as e:
            print(f"Kapak mektubu oluşturma sırasında beklenmeyen hata: {e}")
            return f"Hata: Kapak mektubu oluşturulamadı. Detaylar: {e}" 