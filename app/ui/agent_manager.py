import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    from ..job_agent_extenction import create_agent as create_linkedin_agent
    from ..job_details_agent import create_job_file_analyzer_agent
    from ..resume_agent import create_resume_analysis_agent
    from ..cover_letter_agent_all import create_cover_letter_agent
    from ..agent_jobs_random_link import create_job_analysis_agent as create_random_job_agent
    from ..job_compatibility_agent import create_job_compatibility_agent
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from job_agent_extenction import create_agent as create_linkedin_agent
    from job_details_agent import create_job_file_analyzer_agent
    from resume_agent import create_resume_analysis_agent
    from cover_letter_agent_all import create_cover_letter_agent
    from agent_jobs_random_link import create_job_analysis_agent as create_random_job_agent
    from job_compatibility_agent import create_job_compatibility_agent


class AgentManager:
    def __init__(self):
        self.job_results_path = Path("Jobs/Job_Results")
        self.resume_path = Path("Jobs/Resumes")
        self.analysis_path = Path("Jobs/Resume_Analysis")
        self.cover_letter_path = Path("Jobs/Cover_Letters")
        self.job_analysis_path = Path("Jobs/Job_Analysis")
        for path in [self.job_results_path, self.resume_path, self.analysis_path, 
                    self.cover_letter_path, self.job_analysis_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def _run_async(self, coro):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    
    async def get_linkedin_agent(self):
        return await create_linkedin_agent()
    
    async def get_job_analyzer_agent(self):
        return await create_job_file_analyzer_agent()
    
    async def get_job_file_analyzer_agent(self):
        return await create_job_file_analyzer_agent()
    
    async def get_resume_agent(self):
        return await create_resume_analysis_agent()
    
    async def get_cover_letter_agent(self):
        return await create_cover_letter_agent()
    
    async def get_random_job_agent(self):
        return await create_random_job_agent()
    
    async def get_job_compatibility_agent(self):
        return await create_job_compatibility_agent()
    
    def get_available_job_files(self) -> list:
        try:
            if not self.job_results_path.exists():
                return ["Henüz iş ilanı dosyası yok"]
            json_files = [f.name for f in self.job_results_path.glob("*.json") if f.is_file()]
            json_files.sort(key=lambda x: (self.job_results_path / x).stat().st_mtime, reverse=True)
            
            if not json_files:
                return ["Henüz iş ilanı dosyası yok"]
            
            return ["Dosya seçin..."] + json_files
            
        except Exception as e:
            return [f"Hata: {str(e)}"]
