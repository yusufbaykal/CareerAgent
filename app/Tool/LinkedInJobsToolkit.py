from typing import Dict, List
import json
import random
import time
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
from agno.tools import Toolkit
from Tool.ContentCache import cache
from agno.utils.log import logger

class LinkedInJobsToolkit(Toolkit):

    BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
    
    def __init__(self):
        super().__init__(name="linkedin_jobs")
        self.batch_size = 25
        self.register(self.search_jobs)
    
    def search_jobs(self, 
                   command: str = "", 
                   keyword: str = "software developer", 
                   location: str = "Türkiye", 
                   date_since_posted: str = "past week", 
                   job_type: str = "", 
                   limit: int = 50) -> str:
        if command and command.strip():
            parsed_params = self._parse_command(command)
            keyword = parsed_params.get("keyword", keyword)
            location = parsed_params.get("location", location)
        
        keyword_clean = keyword.strip() if keyword else ""
        location_clean = location.strip() if location else ""
        
        logger.info(f"LinkedIn araması: '{keyword_clean}' konumunda '{location_clean}'")
        
        try:
            cache_key = f"linkedin_{keyword_clean}_{location_clean}_{date_since_posted}_{job_type}_{limit}"
            
            cached_results = cache.get(cache_key)
            if cached_results:
                logger.info("Önbellekteki sonuçlar döndürülüyor")
                return json.dumps(
                    {"results": cached_results}, 
                    ensure_ascii=False
                )
            
            all_jobs = []
            start = 0
            consecutive_errors = 0
            MAX_CONSECUTIVE_ERRORS = 3
            
            while True:
                try:
                    url = self._construct_url(
                        keyword=keyword_clean,
                        location=location_clean,
                        date_since_posted=date_since_posted,
                        job_type=job_type,
                        start=start
                    )
                    
                    jobs = self._fetch_job_batch(url)
                    
                    if not jobs:
                        break
                        
                    all_jobs.extend(jobs)
                    logger.info(f"{len(jobs)} iş ilanı getirildi. Toplam: {len(all_jobs)}")
                    
                    if limit and len(all_jobs) >= limit:
                        all_jobs = all_jobs[:limit]
                        break
                        
                    consecutive_errors = 0
                    start += self.batch_size
                    
                    time.sleep(2 + random.random())
                    
                except Exception as e:
                    consecutive_errors += 1
                    logger.error(f"Sorgu hatası (deneme {consecutive_errors}): {str(e)}")
                    
                    if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                        logger.error("Maksimum ardışık hata sayısına ulaşıldı. İstek durduruldu.")
                        break
                        
                    time.sleep(2 ** consecutive_errors)
            
            if all_jobs:
                cache.set(cache_key, all_jobs)
                
            logger.info(f"LinkedIn aramasında {len(all_jobs)} sonuç bulundu")
            
            return json.dumps(
                {"results": all_jobs}, 
                ensure_ascii=False
            )
            
        except Exception as e:
            logger.error(f"LinkedIn iş araması hatası: {e}")
            return json.dumps(
                {"error": f"LinkedIn araması sırasında hata oluştu: {str(e)}"}, 
                ensure_ascii=False
            )
    
    def _parse_command(self, command: str) -> Dict[str, str]:
        params = {
            "keyword": "software developer",
            "location": "Türkiye"
        }
        
        command = command.strip()
        if " in " in command:
            parts = command.split(" in ", 1)
            params["keyword"] = parts[0].strip()
            params["location"] = parts[1].strip()
        else:
            params["keyword"] = command
                
        return params
    
    def _construct_url(self, 
                      keyword: str, 
                      location: str, 
                      date_since_posted: str,
                      job_type: str, 
                      start: int) -> str:
        params = {}
        
        if keyword:
            params['keywords'] = keyword
            
        if location:
            params['location'] = location
            
        date_param = self._get_date_since_posted_param(date_since_posted)
        if date_param:
            params['f_TPR'] = date_param
            
        job_type_param = self._get_job_type_param(job_type)
        if job_type_param:
            params['f_JT'] = job_type_param
            
        params['start'] = str(start)
            
        return self.BASE_URL + urlencode(params)
        
    def _fetch_job_batch(self, url: str) -> List[Dict[str, str]]:
        headers = {
            "User-Agent": self._random_user_agent(),
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return self._parse_job_list(response.text)
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP isteği başarısız: {e}")
            raise Exception(f"API isteği başarısız: {e}")
    
    def _parse_job_list(self, html: str) -> List[Dict[str, str]]:
        soup = BeautifulSoup(html, "lxml")
        job_elements = soup.find_all("li")
        logger.info(f"{len(job_elements)} iş ilanı elementi bulundu")
        
        jobs = []
        for idx, element in enumerate(job_elements):
            try:
                title_el = element.find(class_="base-search-card__title")
                company_el = element.find(class_="base-search-card__subtitle")
                location_el = element.find(class_="job-search-card__location")
                time_el = element.find("time")
                job_url_el = element.find("a", class_="base-card__full-link")
                
                if not title_el or not company_el:
                    continue

                job = {
                    "position": title_el.get_text(strip=True),
                    "company": company_el.get_text(strip=True),
                    "location": location_el.get_text(strip=True) if location_el else "",
                    "date": time_el["datetime"] if time_el and time_el.has_attr("datetime") else "",
                    "jobUrl": job_url_el["href"] if job_url_el and job_url_el.has_attr("href") else "",
                }
                jobs.append(job)
                
                if idx < 5:
                    logger.info(f"İş ilanı: {job['position']} @ {job['company']}")
                    
            except Exception as err:
                logger.warning(f"İş ilanı ayrıştırma hatası (indeks {idx}): {err}")
                
        logger.info(f"Toplam {len(jobs)} geçerli iş ilanı ayrıştırıldı")
        return jobs
    
    def _random_user_agent(self) -> str:
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_4) AppleWebKit/605.1.15 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/92.0.4515.107 Safari/537.36"
        ]
        return random.choice(agents)
        
    def _get_date_since_posted_param(self, date_since_posted: str) -> str:
        mapping = {
            "past week": "r604800",
            "past month": "r2592000",
            "24hr": "r86400",
            "week": "r604800",
            "month": "r2592000",
            "day": "r86400"
        }
        return mapping.get(date_since_posted.lower(), "")
        
    def _get_job_type_param(self, job_type: str) -> str:
        mapping = {
            "full time": "F",
            "part time": "P",
            "contract": "C",
            "temporary": "T",
            "internship": "I",
            "full-time": "F",
            "part-time": "P"
        }
        return mapping.get(job_type.lower(), "")