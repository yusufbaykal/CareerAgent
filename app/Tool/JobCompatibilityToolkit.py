from pathlib import Path
import json
from agno.tools import Toolkit
from agno.utils.log import logger
from typing import Optional, List
from datetime import datetime


class JobCompatibilityToolkit(Toolkit):
    
    def __init__(self):
        super().__init__(name="job_compatibility_tools")
        self.job_analysis_dir = Path("Jobs/Job_Analysis")
        self.resume_analysis_dir = Path("Jobs/Resume_Analysis")
        self.compatibility_results_dir = Path("Jobs/Job_Compatibility")
        self.compatibility_results_dir.mkdir(exist_ok=True, parents=True)
        
        self.register(self.load_job_analysis)
        self.register(self.load_resume_analysis)
        self.register(self.analyze_compatibility)
        self.register(self.save_compatibility_report)
    
    def _find_analysis_file(self, filename: str, search_dirs: List[Path]) -> Optional[Path]:
        possible_paths = []
        
        for directory in search_dirs:
            possible_paths.append(directory / filename)
            if not filename.endswith('.json'):
                possible_paths.append(directory / f"{filename}.json")
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def _load_analysis_file(self, filename: str, search_dirs: List[Path], file_type: str) -> str:
        try:
            file_path = self._find_analysis_file(filename, search_dirs)
            
            if not file_path:
                return json.dumps({"error": f"{file_type} dosyası bulunamadı: {filename}"})
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            logger.info(f"{file_type} dosyası yüklendi: {file_path}")
            return json.dumps(data, ensure_ascii=False)
                
        except json.JSONDecodeError as e:
            error_msg = f"{file_type} JSON formatı geçersiz: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
        except Exception as e:
            error_msg = f"{file_type} yükleme hatası: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
        
    def load_job_analysis(self, job_analysis_file: str) -> str:
        search_dirs = [self.job_analysis_dir]
        return self._load_analysis_file(job_analysis_file, search_dirs, "İş analizi")
    
    def load_resume_analysis(self, resume_analysis_file: str) -> str:
        search_dirs = [self.resume_analysis_dir]
        return self._load_analysis_file(resume_analysis_file, search_dirs, "CV analizi")
    
    def analyze_compatibility(self, job_data: str, resume_data: str) -> str:
        try:
            job_info = self._parse_json_safely(job_data, "iş verisi")
            if isinstance(job_info, str) and job_info.startswith('{"error"'):
                return job_info
                
            resume_info = self._parse_json_safely(resume_data, "CV verisi")
            if isinstance(resume_info, str) and resume_info.startswith('{"error"'):
                return resume_info
            
            compatibility_analysis = {
                "job_requirements": job_info,
                "candidate_profile": resume_info,
                "analysis_instruction": {
                    "task": "İş ilanı gereksinimlerini CV ile karşılaştır ve uygunluk analizi yap",
                    "scoring_system": "10 üzerinden uygunluk skoru ver",
                    "analysis_criteria": [
                        "Teknik beceriler uyumu",
                        "Deneyim seviyesi uygunluğu", 
                        "Eğitim geçmişi uygunluğu",
                        "İş türü deneyimi",
                        "Sektör deneyimi",
                        "Dil yeterlilikleri",
                        "Sertifikalar ve ek beceriler",
                        "Genel uygunluk"
                    ],
                    "output_format": {
                        "overall_score": "1-10 arası genel uygunluk skoru",
                        "technical_skills_score": "1-10 teknik beceri skoru",
                        "experience_score": "1-10 deneyim skoru", 
                        "education_score": "1-10 eğitim skoru",
                        "strengths": ["Güçlü yönler listesi"],
                        "weaknesses": ["Gelişim alanları listesi"],
                        "recommendations": ["Adaya öneriler"],
                        "detailed_analysis": "Detaylı uygunluk raporu"
                    }
                }
            }
            
            logger.info("İş uygunluğu analizi için veriler hazırlandı")
            return json.dumps(compatibility_analysis, ensure_ascii=False)
            
        except Exception as e:
            error_msg = f"Uygunluk analizi hatası: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    def _parse_json_safely(self, data: str, data_type: str):
        if isinstance(data, dict):
            return data
            
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError as e:
                error_msg = f"Geçersiz {data_type} JSON formatı: {str(e)}"
                logger.error(error_msg)
                return json.dumps({"error": error_msg})
        
        return json.dumps({"error": f"Beklenmeyen {data_type} veri tipi"})
    
    def save_compatibility_report(self, compatibility_report: str, workflow_id: str, job_title: str = None, candidate_name: str = None) -> str:
        try:
            from datetime import datetime
            
            filename = f"compatibility_{workflow_id}.json"
            file_path = self.compatibility_results_dir / filename
            
            report_data = self._prepare_report_data(compatibility_report, job_title, candidate_name)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Uygunluk raporu kaydedildi: {file_path}")
            return f"Uygunluk raporu başarıyla '{filename}' dosyasına kaydedildi."
            
        except Exception as e:
            error_msg = f"Rapor kaydetme hatası: {str(e)}"
            logger.error(error_msg)
            return f"Rapor kaydedilirken hata oluştu: {error_msg}"
    
    def _sanitize_filename(self, text: str) -> str:
        if not text:
            return "unknown"
        
        safe_text = "".join(c for c in text if c.isalnum() or c in (' ', '-', '_')).strip()
        
        safe_text = safe_text.replace(' ', '_')
        
        return safe_text[:50] if safe_text else "unknown"
    
    def _prepare_report_data(self, compatibility_report: str, job_title: str, candidate_name: str) -> dict:
        if isinstance(compatibility_report, str):
            try:
                report_data = json.loads(compatibility_report)
            except json.JSONDecodeError:
                report_data = {"analysis": compatibility_report}
        else:
            report_data = compatibility_report if isinstance(compatibility_report, dict) else {}
        
        report_data["metadata"] = {
            "candidate_name": candidate_name,
            "job_title": job_title,
            "analysis_date": datetime.now().isoformat(),
            "report_type": "job_compatibility_analysis",
            "version": "1.0"
        }
        
        return report_data 