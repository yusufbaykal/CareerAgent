import json
import re
from datetime import datetime
from pathlib import Path


class UIUtils:
    @staticmethod
    def format_resume_analysis(content: str) -> str:
        try:
            if content.strip().startswith('{'):
                json_data = json.loads(content)
                
                formatted = []
                if 'summary' in json_data:
                    formatted.append(f"📝 **Özet:**\n{json_data['summary']}\n")
                
                if 'skills' in json_data:
                    skills = json_data['skills']
                    if isinstance(skills, list):
                        formatted.append(f"🔧 **Yetenekler:**\n• " + "\n• ".join(skills) + "\n")
                    else:
                        formatted.append(f"🔧 **Yetenekler:**\n{skills}\n")
                
                if 'experience' in json_data:
                    formatted.append(f"💼 **Deneyim:**\n{json_data['experience']}\n")
                
                if 'education' in json_data:
                    formatted.append(f"🎓 **Eğitim:**\n{json_data['education']}\n")
                
                if 'recommendations' in json_data:
                    formatted.append(f"💡 **Öneriler:**\n{json_data['recommendations']}\n")
                
                if 'strengths' in json_data:
                    formatted.append(f"✅ **Güçlü Yönler:**\n{json_data['strengths']}\n")
                
                if 'areas_for_improvement' in json_data:
                    formatted.append(f"🔄 **Gelişim Alanları:**\n{json_data['areas_for_improvement']}\n")
                
                if 'score' in json_data:
                    formatted.append(f"⭐ **Puan:** {json_data['score']}\n")
                
                return "\n".join(formatted) if formatted else content
            
            return content.strip()
            
        except (json.JSONDecodeError, Exception):
            return content.strip()
    
    @staticmethod
    def format_json_properly(content: str) -> str:
        try:
            content = content.strip()
            if content.startswith('{'):
                json_data = json.loads(content)
                formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
                return formatted_json
            
            json_start = content.find('{')
            json_end = content.rfind('}')
            
            if json_start != -1 and json_end != -1 and json_end > json_start:
                json_content = content[json_start:json_end+1]
                json_data = json.loads(json_content)
                formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
                return formatted_json
            
            return None
            
        except (json.JSONDecodeError, Exception):
            return None
    
    @staticmethod
    def count_jobs_from_content(content: str) -> int:
        job_count = 0
        if content:
            matches = re.findall(r'(\d+) iş ilanı getirildi', content)
            if matches:
                job_count = int(matches[-1])
            else:
                numbered_jobs = re.findall(r'^\d+\.\s+\*\*', content, re.MULTILINE)
                job_count = len(numbered_jobs)
                if job_count == 0:
                    linkedin_links = re.findall(r'linkedin\.com/jobs', content)
                    job_count = len(linkedin_links)
        return job_count
    
    @staticmethod
    def count_jobs_from_json(json_filepath: Path) -> int:
        try:
            with open(json_filepath, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            if isinstance(json_data, list):
                return len(json_data)
            elif isinstance(json_data, dict) and 'jobs' in json_data:
                return len(json_data['jobs'])
            elif isinstance(json_data, dict) and 'results' in json_data:
                return len(json_data['results'])
        except:
            pass
        return 0
    
    @staticmethod
    def generate_filename(base_name: str, extension: str = "json") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}.{extension}"
    
    @staticmethod
    def save_txt_file(filepath: Path, content: str, metadata: dict = None):
        with open(filepath, 'w', encoding='utf-8') as f:
            if metadata:
                for key, value in metadata.items():
                    f.write(f"{key}: {value}\n")
                f.write("="*50 + "\n\n")
            f.write(content)
