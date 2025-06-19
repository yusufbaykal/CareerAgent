from pathlib import Path
import json
from typing import Union, Optional, List
from agno.tools import Toolkit
from agno.utils.log import logger
import os


class CoverLetterToolkit(Toolkit):
    def __init__(self):
        super().__init__(name="cover_letter_toolkit")
        self.resume_dir = Path("Jobs/Resumes")
        self.resume_analysis_dir = Path("Jobs/Resume_Analysis")
        self.job_results_dir = Path("Jobs/Job_Results")
        self.job_analysis_dir = Path("Jobs/Job_Analysis")
        self.cover_letter_dir = Path("Jobs/Cover_Letters")
        
        self.register(self.get_resume_analysis)
        self.register(self.get_job_details)
        self.register(self.generate_cover_letter)
        self.register(self.save_cover_letter)
    
    def _find_file(self, file_path: str, possible_dirs: List[Path]) -> Optional[Path]:
        possible_paths = []
        
        possible_paths.append(Path(file_path))
        
        for directory in possible_dirs:
            possible_paths.append(directory / file_path)
            if not file_path.endswith('.json'):
                possible_paths.append(directory / f"{file_path}.json")
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def _load_json_file(self, file_path: str, possible_dirs: List[Path], file_type: str) -> str:
        try:
            found_path = self._find_file(file_path, possible_dirs)
            
            if found_path is None:
                return json.dumps({"error": f"{file_type} dosyası bulunamadı: {file_path}"})
            
            logger.info(f"{file_type} dosyası okunuyor: {found_path}")
            
            with open(found_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            return json.dumps(data, ensure_ascii=False)
                
        except json.JSONDecodeError as e:
            error_msg = f"{file_type} JSON formatı geçersiz: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
        except Exception as e:
            error_msg = f"{file_type} okuma hatası: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
        
    def get_resume_analysis(self, resume_path: str) -> str:
        possible_dirs = [self.resume_analysis_dir, self.resume_dir]
        return self._load_json_file(resume_path, possible_dirs, "Özgeçmiş analizi")
    
    def get_job_details(self, job_file: str, job_id: Optional[int] = None) -> str:
        try:
            possible_dirs = [self.job_analysis_dir, self.job_results_dir]
            result = self._load_json_file(job_file, possible_dirs, "İş ilanı")
            
            if result.startswith('{"error"'):
                return result
            
            job_data = json.loads(result)
            
            if job_id is not None and "results" in job_data:
                jobs = job_data["results"]
                if 0 <= job_id < len(jobs):
                    return json.dumps(jobs[job_id], ensure_ascii=False)
                else:
                    return json.dumps({"error": f"Hata: {job_id} ID'li iş bulunamadı. Toplam {len(jobs)} iş var."})
            
            return result
                
        except Exception as e:
            error_msg = f"İş ilanı işleme hatası: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    def generate_cover_letter(self, resume_data: str, job_data: str) -> str:
        try:
            resume_info = self._parse_json_safely(resume_data, "özgeçmiş")
            if isinstance(resume_info, str):  # Hata mesajı
                return resume_info
                
            job_info = self._parse_json_safely(job_data, "iş ilanı")
            if isinstance(job_info, str):
                return job_info
            
            combined_data = {
                "resume": resume_info,
                "job": job_info,
                "instruction": {
                    "task": "Bu özgeçmiş ve iş ilanı bilgilerine dayanarak profesyonel bir ön yazı (cover letter) oluştur",
                    "requirements": [
                        "Adayın güçlü yönlerini vurgula",
                        "İş gereksinimlerine uygun deneyimleri öne çıkar",
                        "Şirkete ve pozisyona özel içerik ekle",
                        "Profesyonel ve samimi bir ton kullan",
                        "300-400 kelime arası tut"
                    ],
                    "format": "Standart iş başvuru mektubu formatında (başlık, selamlama, gövde, kapanış)"
                }
            }
            
            logger.info("Ön yazı oluşturma verisi hazırlandı")
            return json.dumps(combined_data, ensure_ascii=False)
        
        except Exception as e:
            error_msg = f"Ön yazı hazırlama hatası: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    def _parse_json_safely(self, data: str, data_type: str) -> Union[dict, str]:
        if isinstance(data, dict):
            return data
            
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return json.dumps({"error": f"Geçersiz {data_type} JSON formatı."})
        
        return json.dumps({"error": f"Beklenmeyen {data_type} veri tipi."})
        
    def save_cover_letter(self, cover_letter_text: str, file_name: str) -> str:
        try:
            self.cover_letter_dir.mkdir(exist_ok=True, parents=True)

            if not file_name.endswith('.txt'):
                file_name = f"{file_name}.txt"
                
            file_path = self.cover_letter_dir / file_name
            
            if file_path.exists():
                logger.warning(f"Dosya zaten mevcut, üzerine yazılıyor: {file_path}")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cover_letter_text)
                
            logger.info(f"Ön yazı dosyaya kaydedildi: {file_path}")
            return f"Ön yazı başarıyla {file_path} dosyasına kaydedildi."
            
        except Exception as e:
            error_msg = f"Ön yazı kaydetme hatası: {str(e)}"
            logger.error(error_msg)
            return f"Ön yazı kaydedilirken hata oluştu: {str(e)}"