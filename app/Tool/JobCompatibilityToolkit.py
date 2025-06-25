from pathlib import Path
import json
from agno.tools import Toolkit
from agno.utils.log import logger
from typing import Optional, List
from datetime import datetime
import random
import os
import sys


class JobCompatibilityToolkit(Toolkit):
    
    def __init__(self):
        super().__init__(name="job_compatibility_toolkit")
        self.job_analysis_dir = Path("Jobs/Job_Analysis")
        self.resume_analysis_dir = Path("Jobs/Resume_Analysis")
        self.compatibility_results_dir = Path("Jobs/Job_Compatibility")
        
        for directory in [self.job_analysis_dir, self.resume_analysis_dir, self.compatibility_results_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.register(self.load_job_analysis)
        self.register(self.load_resume_analysis)
        self.register(self.analyze_compatibility)
        self.register(self.save_compatibility_report)
        self.register(self.analyze_single_job_compatibility)
    
    def _safe_encode_decode(self, text: str) -> str:
        if not isinstance(text, str):
            text = str(text)
        
        try:
            text.encode('ascii')
            return text
        except UnicodeEncodeError:
            safe_text = text.encode('ascii', errors='replace').decode('ascii')
            return safe_text
    
    def _safe_json_dumps(self, data, **kwargs) -> str:
        try:
            return json.dumps(data, ensure_ascii=False, **kwargs)
        except UnicodeEncodeError:
            return json.dumps(data, ensure_ascii=True, **kwargs)
    
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
                return self._safe_json_dumps({"error": f"{file_type} file not found: {filename}"})
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            logger.info(f"{file_type} file loaded: {file_path}")
            return self._safe_json_dumps(data)
                
        except json.JSONDecodeError as e:
            error_msg = f"{file_type} JSON format invalid: {str(e)}"
            logger.error(error_msg)
            return self._safe_json_dumps({"error": error_msg})
        except Exception as e:
            error_msg = f"{file_type} loading error: {str(e)}"
            logger.error(error_msg)
            return self._safe_json_dumps({"error": error_msg})
        
    def load_job_analysis(self, job_analysis_file: str) -> str:
        search_dirs = [self.job_analysis_dir]
        return self._load_analysis_file(job_analysis_file, search_dirs, "Job analysis")
    
    def load_resume_analysis(self, resume_analysis_file: str) -> str:
        search_dirs = [self.resume_analysis_dir]
        return self._load_analysis_file(resume_analysis_file, search_dirs, "Resume analysis")
    
    def analyze_compatibility(self, job_data: str, resume_data: str) -> str:
        try:
            job_info = self._parse_json_safely(job_data, "job data")
            if isinstance(job_info, str) and job_info.startswith('{"error"'):
                return job_info
                
            resume_info = self._parse_json_safely(resume_data, "resume data")
            if isinstance(resume_info, str) and resume_info.startswith('{"error"'):
                return resume_info
            
            detailed_analysis_prompt = f"""
            You are a Job Compatibility Analysis Expert. Perform comprehensive candidate evaluation for ALL available job postings.

            ALL JOB POSTINGS DATA:
            {self._safe_json_dumps(job_info, indent=2)}

            CANDIDATE CV ANALYSIS:
            {self._safe_json_dumps(resume_info, indent=2)}

            TASK: Analyze candidate compatibility across ALL available job postings and provide:
            1. Overall compatibility assessment for the candidate across all positions
            2. Average compatibility scores across all jobs
            3. Best matching jobs identification
            4. General strengths and weaknesses analysis
            5. Comprehensive recommendations for the candidate

            DETAILED SCORING CRITERIA (out of 10):

            1. **Technical Skills (25% weight)**:
               - Programming languages, frameworks, technologies alignment with job requirements
               - Software tools, database technologies, cloud platforms experience
               - Technical certifications and specialized skills match

            2. **Experience Level (25% weight)**:
               - Required years of experience vs candidate's total experience comparison
               - Similar position working experience
               - Project management and leadership experience (if required)

            3. **Education Background (15% weight)**:
               - Minimum education level requirement compatibility
               - Education field relevance to the job
               - Additional courses, certifications, postgraduate education

            4. **Sector Experience (15% weight)**:
               - Relevant sector (finance, e-commerce, healthcare etc.) working experience
               - Sector knowledge and domain expertise
               - Familiarity with sector-specific tools and processes

            5. **Language Skills (10% weight)**:
               - Required language skills (English, Turkish etc.)
               - International project working experience
               - Multilingual environment communication ability

            6. **Additional Skills and Soft Skills (10% weight)**:
               - Soft skills mentioned in job postings (teamwork, analytical thinking etc.)
               - Leadership, project management, communication skills
               - Additional certificates, patents, publications, open source contributions

            REQUIRED JSON OUTPUT FORMAT:
            {{
                "overall_score": "X/10",
                "technical_skills_score": "X/10", 
                "experience_score": "X/10",
                "education_score": "X/10",
                "sector_experience_score": "X/10",
                "language_skills_score": "X/10",
                "soft_skills_score": "X/10",
                "best_matching_jobs": [
                    "Job Title 1 - Company 1 (Score: X/10)",
                    "Job Title 2 - Company 2 (Score: X/10)",
                    "Job Title 3 - Company 3 (Score: X/10)"
                ],
                "strengths": [
                    "Cross-cutting strength applicable to multiple positions with evidence",
                    "Technical expertise that appears in multiple job requirements",
                    "Experience aspect that strengthens candidacy across positions"
                ],
                "weaknesses": [
                    "Common gap across multiple job postings with impact assessment", 
                    "Skill or experience area needing development for better job market fit",
                    "Knowledge domain that limits opportunities across available positions"
                ],
                "recommendations": [
                    "Priority skill development recommendation with highest impact across jobs",
                    "Learning path or certification suggestion that opens multiple opportunities", 
                    "Experience gaining advice that improves overall market positioning"
                ],
                "detailed_analysis": "Comprehensive analysis covering: 1) Overall market fit assessment across all available positions, 2) Key strengths that appear consistently valuable, 3) Common gaps limiting opportunities, 4) Market positioning evaluation, 5) Strategic recommendations for improving candidacy across job market. Include average scores, best opportunities, and career development pathway suggestions."
            }}

            ANALYSIS QUALITY REQUIREMENTS:
            - Analyze patterns across ALL available job postings
            - Identify commonly required skills and candidate gaps
            - Calculate average/weighted scores across all positions
            - Provide market-level insights and recommendations
            - Reference specific job titles and companies in analysis
            - Give strategic career development advice
            - Prioritize recommendations by impact across multiple opportunities

            CRITICAL: Return ONLY the JSON response, no additional text or explanations.
            """

            compatibility_analysis = {
                "job_requirements": job_info,
                "candidate_profile": resume_info,
                "analysis_instruction": detailed_analysis_prompt.strip(),
                "analysis_type": "multi_job_detailed_compatibility",
                "metadata": {
                    "analysis_level": "detailed_multiagent_quality",
                    "job_count": len(job_info) if isinstance(job_info, dict) else 1,
                    "scoring_categories": 6,
                    "output_format": "structured_json_with_market_analysis"
                }
            }
            
            logger.info("Detailed multi-job compatibility analysis data prepared")
            return self._safe_json_dumps(compatibility_analysis, indent=2)
            
        except Exception as e:
            error_msg = f"Compatibility analysis error: {str(e)}"
            logger.error(error_msg)
            return self._safe_json_dumps({"error": error_msg})
    
    def _parse_json_safely(self, data: str, data_type: str):
        if isinstance(data, dict):
            return data
            
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError as e:
                error_msg = f"Invalid {data_type} JSON format: {str(e)}"
                logger.error(error_msg)
                return self._safe_json_dumps({"error": error_msg})
        
        return self._safe_json_dumps({"error": f"Unexpected {data_type} data type"})
    
    def save_compatibility_report(self, compatibility_report: str, workflow_id: str = None, job_title: str = None, candidate_name: str = None) -> str:
        try:
            from datetime import datetime
            import random
            
            if not workflow_id:
                workflow_id = str(random.randint(10, 99))
            
            if job_title and job_title != "Bilinmeyen Pozisyon":
                safe_job_title = self._sanitize_filename(job_title)
                filename = f"compatibility_{workflow_id}_{safe_job_title}.json"
            else:
                filename = f"compatibility_{workflow_id}.json"
                
            file_path = self.compatibility_results_dir / filename
            
            report_data = self._prepare_report_data(compatibility_report, job_title, candidate_name)
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self._safe_json_dumps(report_data, indent=2))
            except UnicodeEncodeError:
                with open(file_path, 'w', encoding='ascii', errors='replace') as f:
                    f.write(json.dumps(report_data, ensure_ascii=True, indent=2))
                
            logger.info(f"Uygunluk raporu kaydedildi: {file_path}")
            
            success_msg = f"Uygunluk raporu başarıyla '{filename}' dosyasına kaydedildi."
            if job_title and job_title != "Bilinmeyen Pozisyon":
                success_msg += f"\n🎯 Analiz edilen iş: {job_title}"
                
            return success_msg
            
        except UnicodeEncodeError as e:
            error_msg = f"Encoding hatası: Türkçe karakterler desteklenmiyor"
            logger.error(f"Encoding hatası: {str(e)}")
            return f"Encoding hatası: {error_msg}"
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
                report_data = {
                    "analysis": compatibility_report,
                    "raw_content": True,
                    "note": "Raw content - JSON parse edilemedi"
                }
        else:
            report_data = compatibility_report if isinstance(compatibility_report, dict) else {}
        
        report_data["metadata"] = {
            "candidate_name": candidate_name or "Bilinmeyen Aday",
            "job_title": job_title or "Bilinmeyen Pozisyon",
            "analysis_date": datetime.now().isoformat(),
            "report_type": "job_compatibility_analysis",
            "version": "1.0",
            "encoding": "utf-8"
        }
        
        return report_data 
    
    def analyze_single_job_compatibility(self, job_analysis_data: str, resume_data: str, job_index: int = None, job_title: str = None) -> str:
        try:
            job_data = self._parse_json_safely(job_analysis_data, "job_analysis")
            if isinstance(job_data, str):
                return job_data
            
            resume_parsed = self._parse_json_safely(resume_data, "resume")
            if isinstance(resume_parsed, str):
                return resume_parsed
            
            selected_job = None
            company_name = "Unknown Company"
            position_name = "Unknown Position"
            
            if job_index is not None:
                if "results" in job_data:
                    jobs_list = job_data["results"]
                    if 0 <= job_index < len(jobs_list):
                        selected_job = jobs_list[job_index]
                        company_name = selected_job.get("company_information", "Unknown Company")
                        position_name = selected_job.get("position_details", "Unknown Position")
                        
                        if company_name and company_name != "Unknown Company":
                            company_name = company_name.split(",")[0].split(".")[0].strip()
                        
                        if position_name and position_name != "Unknown Position":
                            if "," in position_name:
                                position_name = position_name.split(",")[0].strip()
                else:
                    job_items = list(job_data.items())
                    if 0 <= job_index < len(job_items):
                        job_key, job_value = job_items[job_index]
                        selected_job = job_value
                        if " - " in job_key:
                            position_name, company_name = job_key.split(" - ", 1)
                        else:
                            position_name = job_key
                            if isinstance(job_value, dict):
                                company_name = job_value.get("company_information", "Unknown Company")
                            else:
                                company_name = "Unknown Company"
            
            elif job_title:
                if "results" in job_data:
                    jobs_list = job_data["results"]
                    for job in jobs_list:
                        job_company = job.get("company_information", "").split(",")[0].split(".")[0].strip()
                        job_position = job.get("position_details", "").split(",")[0].strip()
                        if job_title in f"{job_company} - {job_position}" or job_title == job_company or job_title == job_position:
                            selected_job = job
                            company_name = job_company
                            position_name = job_position
                            break
                elif job_title in job_data:
                    selected_job = job_data[job_title]
                    if " - " in job_title:
                        position_name, company_name = job_title.split(" - ", 1)
                    else:
                        position_name = job_title
                        if isinstance(selected_job, dict):
                            company_name = selected_job.get("company_information", "Unknown Company")
                        else:
                            company_name = "Unknown Company"
            
            if not selected_job:
                return self._safe_json_dumps({"error": "Specified job not found"})
            
            detailed_analysis_prompt = f"""
            You are a Job Compatibility Analysis Expert. Perform a comprehensive candidate evaluation for this specific position.

            POSITION: {position_name}
            COMPANY: {company_name}

            JOB ANALYSIS DATA:
            {self._safe_json_dumps(selected_job, indent=2)}

            CANDIDATE CV ANALYSIS:
            {self._safe_json_dumps(resume_parsed, indent=2)}

            DETAILED SCORING CRITERIA (out of 10):

            1. **Technical Skills (25% weight)**:
               - Programming languages, frameworks, technologies alignment with job requirements
               - Software tools, database technologies, cloud platforms experience
               - Technical certifications and specialized skills match

            2. **Experience Level (25% weight)**:
               - Required years of experience vs candidate's total experience comparison
               - Similar position working experience
               - Project management and leadership experience (if required)

            3. **Education Background (15% weight)**:
               - Minimum education level requirement compatibility
               - Education field relevance to the job
               - Additional courses, certifications, postgraduate education

            4. **Sector Experience (15% weight)**:
               - Relevant sector (finance, e-commerce, healthcare etc.) working experience
               - Sector knowledge and domain expertise
               - Familiarity with sector-specific tools and processes

            5. **Language Skills (10% weight)**:
               - Required language skills (English, Turkish etc.)
               - International project working experience
               - Multilingual environment communication ability

            6. **Additional Skills and Soft Skills (10% weight)**:
               - Soft skills mentioned in job posting (teamwork, analytical thinking etc.)
               - Leadership, project management, communication skills
               - Additional certificates, patents, publications, open source contributions

            SCORE EVALUATION GUIDE:
            - **8-10 points**: Excellent match - Definitely should apply, very high success chance
            - **6-7 points**: Good match - Should apply, good success chance
            - **4-5 points**: Medium match - Can apply after addressing gaps, medium success chance  
            - **1-3 points**: Low match - Not suitable for this position, should look for different opportunities

            REQUIRED JSON OUTPUT FORMAT:
            {{
                "overall_score": "X/10",
                "technical_skills_score": "X/10", 
                "experience_score": "X/10",
                "education_score": "X/10",
                "sector_experience_score": "X/10",
                "language_skills_score": "X/10",
                "soft_skills_score": "X/10",
                "strengths": [
                    "Specific strength with job requirement alignment and evidence from CV",
                    "Another strength with concrete examples and technologies mentioned",
                    "Technical expertise that directly matches job requirements"
                ],
                "weaknesses": [
                    "Specific gap or missing skill required for this job with clear reasoning", 
                    "Area needing development with assessment of impact on job performance",
                    "Missing experience or knowledge domain affecting suitability"
                ],
                "recommendations": [
                    "Actionable recommendation to address specific gap with timeline",
                    "Learning path or certification suggestion with specific resources", 
                    "Skill development or experience gaining advice with practical steps"
                ],
                "detailed_analysis": "Comprehensive analysis covering: 1) Overall assessment summary, 2) Key technical strengths and how they align with job needs, 3) Main experience gaps and their impact, 4) Sector fit evaluation, 5) Final recommendation with reasoning about success probability. Include specific technology names, experience numbers, and concrete examples from both job requirements and candidate background."
            }}

            ANALYSIS QUALITY REQUIREMENTS:
            - Use specific technology/skill names from both job posting and CV
            - Provide concrete reasoning for each numerical score
            - Assess gap-closing timeframes realistically (weeks/months)
            - Reference specific job requirements and candidate experiences
            - Include numerical data when available (years of experience, project results)
            - Make recommendations actionable with specific next steps
            - Write detailed analysis with clear structure and logical flow

            CRITICAL: Return ONLY the JSON response, no additional text or explanations.
            """
            
            single_compatibility = {
                "job_title": f"{company_name} - {position_name}",
                "company_name": company_name,
                "position_name": position_name,
                "selected_job_data": selected_job,
                "resume_data": resume_parsed,
                "analysis_instruction": detailed_analysis_prompt.strip(),
                "analysis_type": "single_job_detailed_compatibility",
                "metadata": {
                    "job_index": job_index,
                    "analysis_level": "detailed_multiagent_quality",
                    "scoring_categories": 6,
                    "output_format": "structured_json"
                }
            }
            
            logger.info(f"Detailed single job compatibility analysis prepared: {company_name} - {position_name}")
            return self._safe_json_dumps(single_compatibility)
            
        except Exception as e:
            error_msg = f"Single job compatibility analysis error: {str(e)}"
            logger.error(error_msg)
            return self._safe_json_dumps({"error": error_msg}) 