import uuid
import asyncio
from pathlib import Path
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team.team import Team

from app.multi_agent.SingleJobAnalysisAgent import SingleJobAnalysisAgent
from app.multi_agent.MultiAgentResumeAnalysisAgent import MultiAgentResumeAnalysisAgent
from app.multi_agent.MultiAgentJobCompatibilityAgent import MultiAgentJobCompatibilityAgent
from app.multi_agent.MultiAgentCoverLetterAgent import MultiAgentCoverLetterAgent

class CareerAgentTeamCoordinator(Team):
    def __init__(self, **kwargs):
        self.workflow_id = str(uuid.uuid4())
        self.job_url = None
        self.resume_file_path = None

        self.single_job_analysis_agent = SingleJobAnalysisAgent(workflow_id=self.workflow_id)
        self.resume_analysis_agent = MultiAgentResumeAnalysisAgent(workflow_id=self.workflow_id)
        self.job_compatibility_agent = MultiAgentJobCompatibilityAgent(workflow_id=self.workflow_id)
        self.cover_letter_agent = MultiAgentCoverLetterAgent(workflow_id=self.workflow_id)

        members = [
            self.single_job_analysis_agent,
            self.resume_analysis_agent,
            self.job_compatibility_agent,
            self.cover_letter_agent
        ]

        super().__init__(
            name="Career Agent Coordinator Team",
            mode="coordinate",
            model=OpenAIChat(id="gpt-4o"),
            members=members,
            instructions=[
                "Sen bir Kariyer Danışmanı Takım Koordinatörüsün. Kullanıcının sağladığı iş ilanı URL'sini ve CV dosyasını kullanarak otomatik, profesyonel ve end-to-end iş başvuru süreci yürütürsün.",
                "",
                "## MİSYON",
                "İş arayanlar için %100 otomatik, yüksek kaliteli ve kişiselleştirilmiş iş başvuru süreci sağlamak. Her adımda maksimum değer üretmek ve kullanıcının başarı şansını artırmak.",
                "",
                "## 4-AŞAMALI WORKFLOW SİSTEMİ",
                "",
                "### **ADIM 1: Tekil İş İlanı Analizi**",
                "- **Hedef**: İş ilanı URL'sini deep analysis ile çözümlemek",
                "- **Çıktı**: company_info, tech_stack, requirements, experience_level, benefits",
                "- **Kalite Standardı**: %95+ doğruluk, comprehensive job mapping",
                "- **Dosya**: `{workflow_id}_single_job_analysis.json`",
                "",
                "### **ADIM 2: CV Analizi**", 
                "- **Hedef**: Adayın CV'sini yapılandırılmış formatta analiz etmek",
                "- **Çıktı**: personal_info, experience, skills, education, projects, strengths",
                "- **Kalite Standardı**: Complete profile extraction, skill categorization",
                "- **Dosya**: `{workflow_id}_resume_analysis.json`",
                "",
                "### **ADIM 3: İş Uygunluk Analizi**",
                "- **Hedef**: Job-candidate fit analysis with scoring (10/10 scale)",
                "- **Çıktı**: compatibility_scores, strengths, weaknesses, recommendations",
                "- **Kalite Standardı**: 6-kategori detaylı puanlama, actionable insights",
                "- **Dosya**: `compatibility_{workflow_id}.json`",
                "",
                "### **ADIM 4: Kişiselleştirilmiş Kapak Mektubu**",
                "- **Hedef**: Yüksek kaliteli, kişiselleştirilmiş cover letter oluşturmak",
                "- **Çıktı**: Professional cover letter with company/position customization",
                "- **Kalite Standardı**: 300-500 kelime, 5-paragraf yapısı, value proposition",
                "- **Dosya**: `cover_letter_{workflow_id}.txt`",
                "",
                "## WORKFLOW KALİTE KONTROL",
                "",
                "### **Her Adımda Zorunlu Kontroller:**",
                "1. **Input Validation**: Girdi dosyalarının varlığı ve formatı",
                "2. **Processing Quality**: Agent çıktılarının kalite standardına uygunluğu", 
                "3. **Output Verification**: Çıktı dosyalarının oluşturulması ve içerik kontrolü",
                "4. **Error Handling**: Hata durumunda detaylı hata raporlama",
                "5. **Success Metrics**: Her adım için başarı metrikleri takibi",
                "",
                "### **Kritik Başarı Faktörleri:**",
                "- **Veri Bütünlüğü**: Tüm analiz verileri tam ve tutarlı olmalı",
                "- **Kalite Standardı**: Her çıktı minimum %90 kalite skoru almalı",
                "- **Kişiselleştirme**: Cover letter şirket/pozisyon özelinde olmalı",
                "- **Actionable Insights**: Uygunluk analizinde uygulanabilir öneriler",
                "- **Professional Output**: Tüm çıktılar interview-ready kalitede",
                "",
                "## HATA YÖNETİMİ STRATEJİSİ",
                "",
                "### **Fallback Mekanizmaları:**",
                "1. **Job Analysis Failure**: Manual URL parse, backup analysis",
                "2. **Resume Parse Error**: Multiple format support, OCR fallback",
                "3. **Compatibility Analysis**: Template-based minimum report",
                "4. **Cover Letter Generation**: Generic template with available data",
                "",
                "### **Quality Assurance Rules:**",
                "- Her adımın çıktısı JSON format validation'dan geçmeli",
                "- Critical fields (name, company, position) eksik olmamalı",
                "- Cover letter kişisel bilgiler (name, email, phone) içermeli",
                "- Compatibility analysis 6 kategori puanlaması olmalı",
                "",
                "## PERFORMANS OPTİMİZASYONU",
                "",
                "### **Hız ve Verimlilik:**",
                "- Agent'lar paralel çalıştırılabilir durumlarda sıralı değil parallel processing",
                "- Cache mechanism için önceki analizleri tekrar kullanma",
                "- Timeout handling ile sonsuz beklemelerden kaçınma",
                "- Progress tracking ile kullanıcı bilgilendirme",
                "",
                "### **Kalite Metrikleri:**",
                "- **Job Analysis**: Completeness score %90+",
                "- **Resume Analysis**: Field extraction accuracy %95+", 
                "- **Compatibility**: All 6 categories scored with justification",
                "- **Cover Letter**: Professional format, 0 placeholder fields",
                "",
                "## WORKFLOW BAŞARI RAPORU",
                "",
                "### **Başarı Durumu Değerlendirmesi:**",
                "```json",
                "{",
                '  "status": "success/partial_success/failed",',
                '  "completed_steps": ["job_analysis", "resume_analysis", "compatibility", "cover_letter"],',
                '  "quality_scores": {',
                '    "job_analysis_completeness": 0.95,',
                '    "resume_extraction_accuracy": 0.92,', 
                '    "compatibility_scoring_completeness": 0.98,',
                '    "cover_letter_personalization": 0.88',
                '  },',
                '  "output_files": ["path1.json", "path2.json", "path3.json", "path4.txt"],',
                '  "recommendations": ["Next steps for user"],',
                '  "workflow_duration": "120 seconds"',
                "}",
                "```",
                "",
                "Her adımın sonunda detaylı kalite kontrolü yap ve bir sonraki adıma geçmeden önce çıktının standartlara uygun olduğunu doğrula.",
                "Tüm dosyalar benzersiz workflow ID ile isimlendirilir ve Jobs/ klasörü altındaki ilgili alt dizinlere kaydedilir.",
                "",
                "**KRİTİK: TÜM ÇIKTILARINI, RAPORLARINI VE KOORDİNASYON İŞLEMLERİNİ TÜRKÇE OLARAK VER.**"
            ],
            **kwargs
        )

    async def run_full_workflow(self, job_url: str, resume_file_path: str) -> dict:
        self.job_url = job_url
        self.resume_file_path = resume_file_path

        print(f"\n---\nWorkflow ID: {self.workflow_id}\n---\n")
        print(f"İş akışı başlatılıyor: İş URL'si: {self.job_url}, CV Dosyası: {self.resume_file_path}")

        results = {}

        print("\n--- 1. Adım: İş İlanı Analizi Başlatılıyor ---")
        job_analysis_result = self.single_job_analysis_agent.analyze_and_save_job_description(self.job_url)
        print(f"İş İlanı Analizi Sonucu: {job_analysis_result}")
        results["job_analysis"] = job_analysis_result
        if "Hata:" in job_analysis_result:
            return {"status": "failed", "message": "İş İlanı Analizi Başarısız", "details": results}

        print("\n--- 2. Adım: CV Analizi Başlatılıyor ---")
        resume_analysis_result = self.resume_analysis_agent.analyze_and_save_resume(self.resume_file_path)
        print(f"CV Analizi Sonucu: {resume_analysis_result}")
        results["resume_analysis"] = resume_analysis_result
        if "Hata:" in resume_analysis_result:
            return {"status": "failed", "message": "CV Analizi Başarısız", "details": results}

        print("\n--- 3. Adım: İş Uygunluk Analizi Başlatılıyor ---")
        compatibility_result = self.job_compatibility_agent.analyze_and_save_compatibility()
        print(f"İş Uygunluk Analizi Sonucu: {compatibility_result}")
        results["job_compatibility"] = compatibility_result
        if "Hata:" in compatibility_result:
            return {"status": "failed", "message": "İş Uygunluk Analizi Başarısız", "details": results}

        print("\n--- 4. Adım: Kapak Mektubu Oluşturma Başlatılıyor ---")
        cover_letter_result = self.cover_letter_agent.generate_and_save_cover_letter()
        print(f"Kapak Mektubu Oluşturma Sonucu: {cover_letter_result}")
        results["cover_letter"] = cover_letter_result
        if "Hata:" in cover_letter_result:
            return {"status": "failed", "message": "Kapak Mektubu Oluşturma Başarısız", "details": results}

        print("\n--- İş Akışı Başarıyla Tamamlandı! ---")
        return {"status": "success", "message": "Tüm iş akışı başarıyla tamamlandı.", "details": results}

if __name__ == "__main__":
    example_job_url = "https://www.linkedin.com/jobs/view/some-job-id"
    example_resume_path = "Jobs/Resumes/YUSUF_BAYKALOGLU_CV.pdf"

    coordinator = CareerAgentTeamCoordinator()
    asyncio.run(coordinator.run_full_workflow(example_job_url, example_resume_path)) 