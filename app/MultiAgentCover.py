import os
import asyncio
import argparse
import logging
from pathlib import Path
from agno.utils.log import logger

from agent_jobs_random_link import run_agent as run_job_analysis, generate_filename_from_url
from resume_agent import run_agent as run_resume_analysis
from cover_letter_agent_all import run_agent as run_cover_letter_generation

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class MultiAgentCoverLetterSystem:
    
    def __init__(self):
        for dir_path in ["Jobs/jobs_result","Jobs/resumes", "Jobs/resumes_analysis", "Jobs/cover_letters"]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    async def analyze_job(self, job_url: str) -> str:
        logger.info(f"İş analizi başlatılıyor: {job_url}")
        
        job_filename = generate_filename_from_url(job_url)
        job_result_path = f"Jobs/Job_Results/{job_filename}.json"
        
        analysis_msg = f"{job_url} adresindeki iş ilanını analiz et ve sonuçları {job_result_path} dosyasına kaydet."
        
        await run_job_analysis(analysis_msg)
        
        if not os.path.exists(job_result_path):
            raise FileNotFoundError(f"İş analiz sonucu bulunamadı: {job_result_path}")
            
        logger.info(f"İş analizi tamamlandı: {job_result_path}")
        return job_result_path
    
    async def analyze_resume(self, resume_path: str) -> str:
        logger.info(f"Özgeçmiş analizi başlatılıyor: {resume_path}")

        if not os.path.exists(resume_path):
            raise FileNotFoundError(f"Özgeçmiş dosyası bulunamadı: {resume_path}")
        
        resume_filename = Path(resume_path).stem
        resume_result_path = f"Jobs/Resume_Analysis/{resume_filename}_analysis.json"
        
        resume_file_name = Path(resume_path).name
        expected_path = f"Jobs/Resumes/{resume_file_name}"
        
        if resume_path != expected_path and not os.path.samefile(resume_path, expected_path) if os.path.exists(expected_path) else True:
            os.makedirs("Jobs/Resumes", exist_ok=True)
            import shutil
            shutil.copy2(resume_path, expected_path)
            logger.info(f"Özgeçmiş dosyası kopyalandı: {resume_path} -> {expected_path}")
        else:
            logger.info(f"Özgeçmiş dosyası zaten beklenen konumda: {resume_path}")
        
        analysis_msg = f"{resume_file_name} dosyasını analiz et ve sonuçları {resume_result_path} dosyasına kaydet."
        logger.info(f"Özgeçmiş analiz komutu: {analysis_msg}")
        
        await run_resume_analysis(analysis_msg)
        
        possible_paths = [
            resume_result_path,
            resume_result_path.replace("Resume_Analysis", "resume_analysis"),
            f"Jobs/Resume_Analysis/{resume_filename}_analysis.json",
            f"Jobs/resume_analysis/{resume_filename}_analysis.json"
        ]
        
        result_path = None
        for path in possible_paths:
            if os.path.exists(path):
                result_path = path
                break
        
        if not result_path:
            raise FileNotFoundError(f"Özgeçmiş analiz sonucu bulunamadı. Kontrol edilen yollar: {possible_paths}")
                
        logger.info(f"Özgeçmiş analizi tamamlandı: {result_path}")
        return result_path
        
    async def generate_cover_letter(self, job_analysis_path: str, resume_analysis_path: str) -> str:
        logger.info(f"Cover letter oluşturma başlatılıyor...")
        
        cover_letter = await run_cover_letter_generation(job_analysis_path, resume_analysis_path)
        
        job_filename = Path(job_analysis_path).stem
        resume_filename = Path(resume_analysis_path).stem
        cover_letter_path = f"Jobs/Cover_Letters/cover_letter_{job_filename}_{resume_filename}.txt"
        
        logger.info(f"Cover letter oluşturma tamamlandı: {cover_letter_path}")
        return cover_letter_path
    
    async def run_pipeline(self, job_url: str, resume_path: str) -> str:
        try:
            job_analysis_path = await self.analyze_job(job_url)
            
            resume_analysis_path = await self.analyze_resume(resume_path)
            
            cover_letter_path = await self.generate_cover_letter(job_analysis_path, resume_analysis_path)
            
            logger.info(f"""
            ===========================================
            COVER LETTER OLUŞTURMA TAMAMLANDI
            ===========================================
            İş Analizi: {job_analysis_path}
            Özgeçmiş Analizi: {resume_analysis_path}
            Cover Letter: {cover_letter_path}
            ===========================================
            """)
            
            return cover_letter_path
            
        except Exception as e:
            logger.error(f"Multi-agent sürecinde hata: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise

async def main():
    parser = argparse.ArgumentParser(description='İş URL\'si ve özgeçmişten otomatik cover letter oluştur.')
    parser.add_argument('--job_url', '-j', required=True, help='İş ilanı URL\'si')
    parser.add_argument('--resume', '-r', required=True, help='Özgeçmiş dosyasının yolu')
    args = parser.parse_args()
    
    system = MultiAgentCoverLetterSystem()
    cover_letter_path = await system.run_pipeline(args.job_url, args.resume)
    
    print(f"\nCover letter başarıyla oluşturuldu: {cover_letter_path}")
    print("\nİçeriği görüntülemek için dosyayı açabilirsiniz.")

if __name__ == "__main__":
    asyncio.run(main())