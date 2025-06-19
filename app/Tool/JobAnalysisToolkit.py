from typing import List
import json
from agno.tools import Toolkit
from Tool.ContentCache import cache
from agno.utils.log import logger

class JobAnalysisToolkit(Toolkit):    
    def __init__(self):
        super().__init__(name="job_analysis")
        self.register(self.analyze_job_description)
        self.register(self.extract_job_details)
        self.register(self.compare_jobs)
        
    def analyze_job_description(self, content: str) -> str:
        try:
            if not content or content.startswith('{"error"'):
                return json.dumps({"error": "Geçerli içerik bulunamadı."})
                
            cache_key = f"analysis_{hash(content)}"
            cached = cache.get(cache_key)
            if cached:
                return cached
            
            prepared_content = {
                "content": content,
                "instruction": "Bu iş ilanı içeriğini analiz et ve aşağıdaki yapılandırılmış bilgileri çıkar: "
                "pozisyon, şirket, konum, iş tipi (tam zamanlı, yarı zamanlı vb.), deneyim seviyesi, "
                "gereken beceriler (teknik ve kişisel), sorumluluklar, avantajlar/faydalar, ve gereken eğitim düzeyi"
            }
            
            return json.dumps(prepared_content, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"İş ilanı analizi hatası: {str(e)}")
            return json.dumps({"error": f"İş ilanı analizi hatası: {str(e)}"})
    
    def extract_job_details(self, analysis_result: str) -> str:
        try:
            return analysis_result
            
        except Exception as e:
            logger.error(f"İş detayları çıkartma hatası: {str(e)}")
            return json.dumps({"error": f"İş detayları çıkartma hatası: {str(e)}"})
    
    def compare_jobs(self, job_analyses: List[str]) -> str:
        try:
            if not job_analyses or len(job_analyses) < 2:
                return json.dumps({"error": "Karşılaştırma için en az 2 iş ilanı gereklidir."})
                
            prepared_content = {
                "job_analyses": job_analyses,
                "instruction": "Bu iş ilanlarını karşılaştır ve benzerlikler, farklılıklar ve öne çıkan noktaları belirt."
            }
            
            return json.dumps(prepared_content, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"İş karşılaştırma hatası: {str(e)}")
            return json.dumps({"error": f"İş karşılaştırma hatası: {str(e)}"})