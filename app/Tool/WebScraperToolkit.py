import requests
import json
import re
import random
from bs4 import BeautifulSoup
from agno.tools import Toolkit
from agno.utils.log import logger
from Tool.ContentCache import cache
import dotenv
dotenv.load_dotenv()


class WebScraperToolkit(Toolkit):
    def __init__(self):
        super().__init__(name="web_scraper")
        
        self.register(self.fetch_url_content)
        self.register(self.fetch_linkedin_job)
        self.register(self.search_linkedin_jobs)
        self.register(self.scrape_job_page)

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
            "Accept-Language": "en-US,en;q=0.9"
        }

        
    def fetch_url_content(self, url: str, selector: str = "body") -> str:
        try:
            if not url.startswith(("http://", "https://")):
                error_msg = "Geçersiz URL formatı. URL 'http://' veya 'https://' ile başlamalıdır."
                logger.error(f"❌ {error_msg}")
                return json.dumps({"error": error_msg})
                
            cache_key = f"url_{url}_{selector}"
            cached = cache.get(cache_key)
            if cached:
                logger.info(f"✅ Önbellekten döndürülüyor: {url[:50]}...")
                return cached
                
            headers = {
                "User-Agent": self._get_random_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive"
            }
            
            logger.info(f"🌐 URL çekiliyor: {url}")
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "lxml")
            
            if selector and selector != "body":
                elements = soup.select(selector)
                content = "\n".join([el.get_text(separator="\n", strip=True) for el in elements])
                logger.info(f"📄 CSS seçici '{selector}' ile {len(elements)} element bulundu")
            else:
                content = soup.body.get_text(separator="\n", strip=True) if soup.body else "İçerik bulunamadı"
                logger.info(f"📄 Body içeriği çekildi: {len(content)} karakter")
                
            content = content.strip()
            
            if content:
                cache.set(cache_key, content)
                logger.info(f"✅ İçerik başarıyla çekildi ve önbelleğe kaydedildi")
                
            return content
            
        except requests.exceptions.Timeout:
            error_msg = f"URL erişimi zaman aşımına uğradı: {url}"
            logger.error(f"⏰ {error_msg}")
            return json.dumps({"error": error_msg})
        except requests.exceptions.RequestException as e:
            error_msg = f"URL erişim hatası: {str(e)}"
            logger.error(f"🌐 {error_msg}")
            return json.dumps({"error": error_msg})
        except Exception as e:
            error_msg = f"İçerik çekme hatası: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return json.dumps({"error": error_msg})
    
    def fetch_linkedin_job(self, job_url: str) -> str:
        try:
            logger.info(f"🔍 LinkedIn iş ilanı çekiliyor: {job_url}")
            
            description_selectors = [
                ".description__text",
                ".show-more-less-html",
                ".jobs-box__html-content",
                ".jobs-description__content",
                "[data-automation-id='jobPostingDescription']"
            ]
            
            content = ""
            for selector in description_selectors:
                result = self.fetch_url_content(job_url, selector)
                if not result.startswith('{"error"'):
                    content += result + "\n\n"
                    logger.info(f"✅ İçerik '{selector}' seçici ile çekildi")
                    break
            
            if content:
                title_selectors = [
                    ".jobs-unified-top-card__job-title",
                    ".top-card-layout__title",
                    "h1"
                ]
                
                company_selectors = [
                    ".jobs-unified-top-card__company-name",
                    ".topcard__org-name-link",
                    "[data-automation-id='jobPostingCompanyName']"
                ]
                
                location_selectors = [
                    ".jobs-unified-top-card__bullet",
                    ".topcard__flavor--bullet",
                    "[data-automation-id='jobPostingLocation']"
                ]
                
                job_title = self._try_selectors(job_url, title_selectors)
                company = self._try_selectors(job_url, company_selectors)
                location = self._try_selectors(job_url, location_selectors)
                
                if not job_title.startswith('{"error"'):
                    formatted_content = f"Pozisyon: {job_title}\n\nŞirket: {company}\n\nKonum: {location}\n\n{content}"
                    logger.info(f"✅ LinkedIn iş ilanı başarıyla parse edildi")
                    return formatted_content
                
                return content
            else:
                error_msg = "LinkedIn iş ilanı içeriği çekilemedi."
                logger.error(f"❌ {error_msg}")
                return json.dumps({"error": error_msg})
                
        except Exception as e:
            error_msg = f"LinkedIn iş ilanı çekme hatası: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return json.dumps({"error": error_msg})
    
    def _try_selectors(self, url: str, selectors: list) -> str:
        for selector in selectors:
            result = self.fetch_url_content(url, selector)
            if not result.startswith('{"error"'):
                logger.debug(f"✅ Seçici başarılı: {selector}")
                return result
        
        logger.warning(f"⚠️ Hiçbir seçici başarılı olmadı: {selectors}")
        return "Bulunamadı"
    
    def search_linkedin_jobs(self, keyword: str = "software developer", location: str = "Turkey", limit: int = 10) -> str:
        try:
            logger.info(f"🔍 LinkedIn iş araması: '{keyword}' - '{location}'")
            
            try:
                from Tool.LinkedInJobsToolkit import LinkedInJobsToolkit
                logger.debug("✅ LinkedInJobsToolkit modülü yüklendi")
            except ImportError:
                error_msg = "LinkedInJobsToolkit modülü mevcut değil"
                logger.error(f"❌ {error_msg}")
                return json.dumps({"error": error_msg})
            
            linkedin_toolkit = LinkedInJobsToolkit()
            search_results = linkedin_toolkit.search_jobs(
                keyword=keyword,
                location=location,
                limit=limit
            )
            
            logger.info("✅ LinkedIn arama sonuçları alındı")
            return search_results
            
        except Exception as e:
            error_msg = f"LinkedIn iş araması hatası: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return json.dumps({"error": error_msg})
        
    def scrape_job_page(self, url: str) -> str:
        try:
            if not url or not url.startswith("http"):
                error_msg = "Geçersiz URL formatı"
                logger.error(f"❌ {error_msg}")
                return json.dumps({"error": error_msg})
            
            logger.info(f"🕷️ İş ilanı sayfası kazınıyor: {url}")
            
            response = requests.get(url, headers=self._get_enhanced_headers(), timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "lxml")
            
            job_details = {}
            
            title_selectors = [
                "h1.top-card-layout__title",
                "h1[data-automation-id='jobPostingHeader']",
                "h1.jobs-unified-top-card__job-title",
                "h1"
            ]
            
            company_selectors = [
                "a.topcard__org-name-link",
                "[data-automation-id='jobPostingCompanyName']",
                ".jobs-unified-top-card__company-name a"
            ]
            
            location_selectors = [
                "span.topcard__flavor--bullet",
                "[data-automation-id='jobPostingLocation']",
                ".jobs-unified-top-card__bullet"
            ]
            
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    job_details["title"] = element.get_text(strip=True)
                    logger.debug(f"✅ Başlık bulundu: {job_details['title'][:50]}...")
                    break
            
            for selector in company_selectors:
                element = soup.select_one(selector)
                if element:
                    job_details["company"] = element.get_text(strip=True)
                    logger.debug(f"✅ Şirket bulundu: {job_details['company']}")
                    break
            
            for selector in location_selectors:
                element = soup.select_one(selector)
                if element:
                    job_details["location"] = element.get_text(strip=True)
                    logger.debug(f"✅ Konum bulundu: {job_details['location']}")
                    break
            
            description_selectors = [
                "div.description__text",
                "section.show-more-less-html",
                "[data-automation-id='jobPostingDescription']",
                ".jobs-description__content"
            ]
            
            for selector in description_selectors:
                element = soup.select_one(selector)
                if element:
                    job_details["description"] = element.get_text(strip=True)
                    logger.debug(f"✅ Açıklama bulundu: {len(job_details['description'])} karakter")
                    break
            
            if "description" not in job_details:
                content_sections = soup.find_all(["section", "div"], class_=re.compile("description|job-details|content"))
                if content_sections:
                    combined_content = "\n".join([section.get_text(strip=True) for section in content_sections])
                    job_details["description"] = combined_content
                    logger.debug(f"✅ Fallback ile açıklama bulundu: {len(combined_content)} karakter")
                else:
                    job_details["description"] = "İş açıklaması bulunamadı."
                    logger.warning("⚠️ İş açıklaması bulunamadı")
            
            criteria_section = soup.find("div", class_="description__job-criteria-container")
            if criteria_section:
                criteria_items = criteria_section.find_all("li", class_="description__job-criteria-item")
                criteria_count = 0
                for item in criteria_items:
                    header = item.find(class_="description__job-criteria-subheader")
                    value = item.find(class_="description__job-criteria-text")
                    if header and value:
                        key = header.get_text(strip=True).lower().replace(" ", "_")
                        job_details[key] = value.get_text(strip=True)
                        criteria_count += 1
                
                if criteria_count > 0:
                    logger.debug(f"✅ {criteria_count} iş kriteri bulundu")
            
            logger.info(f"✅ İş ilanı başarıyla kazındı: {len(job_details)} alan")
            return json.dumps(job_details, ensure_ascii=False)
            
        except requests.RequestException as e:
            error_msg = f"HTTP istek hatası: {str(e)}"
            logger.error(f"🌐 {error_msg}")
            return json.dumps({"error": error_msg})
        except Exception as e:
            error_msg = f"Scraping hatası: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return json.dumps({"error": error_msg})
    
    def _get_random_user_agent(self) -> str:
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_4) AppleWebKit/605.1.15 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/93.0.4577.82 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/604.1"
        ]
        
        selected_agent = random.choice(agents)
        logger.debug(f"🎭 User-Agent seçildi: {selected_agent[:50]}...")
        return selected_agent
    
    def _get_enhanced_headers(self) -> dict:
        return {
            "User-Agent": self._get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0"
        }