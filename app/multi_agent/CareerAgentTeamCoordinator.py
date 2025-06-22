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
                "Bu takım, kullanıcının sağladığı iş ilanı URL'sini ve CV dosyasını kullanarak otomatik bir iş başvuru süreci yürütür.",
                "Süreç şu adımları içerir: Tekil İş İlanı Analizi, CV Analizi, İş Uygunluk Analizi ve Kişiselleştirilmiş Ön Yazı Oluşturma.",
                "Her adımın çıktısı, bir sonraki adıma girdi olarak sağlanır ve tüm dosyalar benzersiz bir workflow ID ile isimlendirilir."
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