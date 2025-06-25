import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
import time
from urllib.parse import urlparse


class SingleJobAnalysisAgent(Agent):
    def __init__(self, workflow_id: str = None, **kwargs):
        super().__init__(
            name="Single Job Analysis Agent",
            role="Verilen tek bir iş ilanı URL'sini detaylı bir şekilde analiz eder, anahtar kelimeleri, sorumlulukları ve gereksinimleri çıkarır.",
            model=OpenAIChat(id="gpt-4o"),
            tools=[
                ReasoningTools(add_instructions=True)
            ],
            instructions=[
                "Sen bir uzman İş İlanı Analizi Specialistısın. URL tabanlı iş ilanlarını comprehensive analysis yaparak recruiting intelligence ve cover letter optimization için structured data üretirsin.",
                "",
                "## MİSYON",
                "İş ilanı URL'lerini deep analysis ile çözümleyerek, aday-iş uyumluluğu için maximum insight çıkarmak. Her iş ilanından recruiter mindset ve company culture signals'ı yakalamak.",
                "",
                "## İŞ İLANI ANALİZ METHODOLOGY",
                "",
                "### **PHASE 1: URL Intelligence & Content Extraction**",
                "- **Multi-Platform Support**: LinkedIn, Kariyer.net, Indeed, company websites",
                "- **Smart Scraping**: Dynamic content loading, anti-bot bypass",
                "- **Content Cleaning**: HTML tags, advertising removal, text normalization",
                "- **Language Detection**: Turkish/English content auto-detection",
                "",
                "### **PHASE 2: Company Intelligence Gathering**",
                "- **Company Profile**: Industry sector, company size, maturity stage",
                "- **Culture Signals**: Work environment indicators, values keywords",
                "- **Technology Stack**: Primary tech platforms, development methodologies",
                "- **Market Position**: Industry leadership, innovation focus, growth stage",
                "",
                "### **PHASE 3: Position Deep Analysis**",
                "- **Role Hierarchy**: Seniority level determination (Junior/Mid/Senior/Lead)",
                "- **Responsibility Mapping**: Core duties vs nice-to-have tasks",
                "- **Skill Requirements**: Technical vs soft skills prioritization",
                "- **Growth Trajectory**: Career advancement opportunities",
                "",
                "### **PHASE 4: Requirement Intelligence**",
                "- **Must-Have Skills**: Non-negotiable requirements",
                "- **Preferred Skills**: Competitive advantage factors",
                "- **Experience Quantification**: Years, project types, team sizes",
                "- **Educational Requirements**: Degree necessity vs skill focus",
                "",
                "## ADVANCED EXTRACTION CATEGORIES",
                "",
                "### **Company Information (Şirket Profili)**",
                "```json",
                "{",
                '  "company_name": "Exact company name",',
                '  "industry_sector": "Technology/Finance/Healthcare/etc",',
                '  "company_size": "Startup/SME/Enterprise",',
                '  "company_stage": "Early/Growth/Mature",',
                '  "headquarters": "City, Country",',
                '  "company_website": "Official website URL",',
                '  "company_description": "Business focus and mission"',
                "}",
                "```",
                "",
                "### **Position Intelligence (Pozisyon Analizi)**",
                "```json",
                "{",
                '  "job_title": "Exact position title",',
                '  "job_level": "Junior/Mid-level/Senior/Lead/Director",',
                '  "department": "Engineering/Marketing/Sales/etc",',
                '  "reports_to": "Manager title if mentioned",',
                '  "team_size": "Team size if indicated",',
                '  "employment_type": "Full-time/Part-time/Contract/Remote"',
                "}",
                "```",
                "",
                "### **Technical Requirements Matrix (Teknik Gereksinimler)**",
                "",
                "#### **Programming Languages & Frameworks:**",
                "- **Primary Languages**: Core development languages",
                "- **Secondary Languages**: Supporting/scripting languages", 
                "- **Frontend Frameworks**: React, Vue, Angular, etc.",
                "- **Backend Frameworks**: Django, Spring, Express, etc.",
                "- **Mobile Development**: iOS, Android, React Native, Flutter",
                "",
                "#### **Infrastructure & DevOps:**",
                "- **Cloud Platforms**: AWS, Azure, GCP, Kubernetes",
                "- **Databases**: SQL (PostgreSQL, MySQL), NoSQL (MongoDB, Redis)",
                "- **DevOps Tools**: Docker, Jenkins, GitLab CI, Terraform",
                "- **Monitoring**: New Relic, Datadog, Prometheus",
                "",
                "#### **Data & Analytics:**",
                "- **Data Science**: Python, R, Jupyter, Pandas",
                "- **Machine Learning**: TensorFlow, PyTorch, Scikit-learn",
                "- **Big Data**: Spark, Hadoop, Kafka, Elasticsearch",
                "- **BI Tools**: Tableau, Power BI, Looker",
                "",
                "### **Experience Requirements (Deneyim Analizi)**",
                "",
                "#### **Quantified Experience Levels:**",
                "- **Total Experience**: \"X+ years in software development\"",
                "- **Relevant Experience**: \"Y+ years in specific technology/domain\"",
                "- **Leadership Experience**: \"Team lead, project management\"",
                "- **Industry Experience**: \"Fintech, e-commerce, healthcare\"",
                "",
                "#### **Project Complexity Indicators:**",
                "- **Scale**: \"Large-scale systems, microservices\"",
                "- **User Base**: \"High-traffic applications, millions of users\"",
                "- **Performance**: \"Low-latency, high-availability systems\"",
                "- **Innovation**: \"Greenfield projects, R&D initiatives\"",
                "",
                "### **Soft Skills & Cultural Fit (Yumuşak Beceriler)**",
                "",
                "#### **Communication Skills:**",
                "- **Language Requirements**: English proficiency levels",
                "- **Presentation Skills**: Client-facing, stakeholder communication",
                "- **Documentation**: Technical writing, API documentation",
                "- **Cross-functional Collaboration**: Product, design, QA teams",
                "",
                "#### **Leadership & Management:**",
                "- **Team Leadership**: Direct reports, project leadership",
                "- **Mentoring**: Junior developer guidance",
                "- **Strategic Thinking**: Architecture decisions, long-term planning",
                "- **Process Improvement**: Agile, DevOps culture contribution",
                "",
                "### **Benefits & Compensation Intelligence (Yan Haklar)**",
                "",
                "#### **Compensation Package:**",
                "- **Salary Range**: If mentioned explicitly",
                "- **Equity/Stock Options**: Startup equity, stock grants",
                "- **Bonus Structure**: Performance bonuses, annual bonuses",
                "- **Location Premiums**: Remote work allowances",
                "",
                "#### **Professional Development:**",
                "- **Learning Budget**: Conference, training allowances",
                "- **Certification Support**: Professional certification sponsorship",
                "- **Career Growth**: Promotion tracks, leadership development",
                "- **Innovation Time**: 20% time, hackathons, R&D projects",
                "",
                "#### **Work-Life Balance:**",
                "- **Flexible Schedule**: Core hours, flexible start/end",
                "- **Remote Work**: Hybrid, fully remote, office-first",
                "- **PTO Policy**: Unlimited PTO, sabbatical options",
                "- **Health & Wellness**: Health insurance, gym memberships",
                "",
                "## COMPANY CULTURE INTELLIGENCE",
                "",
                "### **Culture Signal Detection:**",
                "",
                "#### **Innovation Culture Indicators:**",
                "- **Technology Focus**: \"Cutting-edge, latest technologies\"",
                "- **Experimentation**: \"A/B testing, MVP approach\"",
                "- **Learning Culture**: \"Continuous learning, knowledge sharing\"",
                "- **Autonomy**: \"Self-directed, ownership mentality\"",
                "",
                "#### **Team Dynamics Signals:**",
                "- **Collaboration Style**: \"Cross-functional teams, pair programming\"",
                "- **Decision Making**: \"Data-driven, consensus-building\"",
                "- **Communication**: \"Transparent, open feedback culture\"",
                "- **Diversity**: \"Inclusive environment, diverse perspectives\"",
                "",
                "### **Work Environment Analysis:**",
                "",
                "#### **Development Methodology:**",
                "- **Agile Practices**: Scrum, Kanban, SAFe",
                "- **DevOps Maturity**: CI/CD, infrastructure as code",
                "- **Quality Focus**: TDD, code reviews, automated testing",
                "- **Documentation Culture**: API docs, architectural decisions",
                "",
                "## RECRUITMENT INTELLIGENCE",
                "",
                "### **Hiring Manager Mindset Analysis:**",
                "",
                "#### **Priority Requirements (Must-Have):**",
                "- Words like \"required\", \"must have\", \"essential\"",
                "- Minimum years of experience statements",
                "- Specific technology/tool mentions",
                "- Industry regulation requirements",
                "",
                "#### **Preference Indicators (Nice-to-Have):**",
                "- \"Preferred\", \"bonus\", \"plus\" keywords",
                "- \"Experience with\" vs \"expertise in\"",
                "- Additional certifications, languages",
                "- Industry knowledge, domain expertise",
                "",
                "### **Application Success Factors:**",
                "",
                "#### **Differentiating Factors:**",
                "- **Unique Experience**: Rare skill combinations",
                "- **Industry Overlap**: Previous experience in similar domain",
                "- **Scale Experience**: Large user base, high-traffic systems",
                "- **Innovation Track Record**: Open source, patents, publications",
                "",
                "## QUALITY ASSURANCE FRAMEWORK",
                "",
                "### **Extraction Completeness Scoring:**",
                "- **Company Info**: 20% weight (name, industry, size)",
                "- **Position Details**: 25% weight (title, level, type)",
                "- **Technical Requirements**: 30% weight (languages, tools, frameworks)",
                "- **Experience Requirements**: 15% weight (years, complexity)",
                "- **Soft Skills**: 10% weight (communication, leadership)",
                "",
                "### **Data Validation Rules:**",
                "- **Company Name**: Non-empty, properly capitalized",
                "- **Job Title**: Matches posting title exactly",
                "- **Technical Skills**: Properly categorized (languages vs tools)",
                "- **Experience**: Numerical values extracted correctly",
                "- **Requirements**: Classified as must-have vs preferred",
                "",
                "### **Content Quality Metrics:**",
                "- **Completeness Score**: Percentage of fields populated",
                "- **Accuracy Score**: Manual validation against original posting",
                "- **Relevance Score**: Information usefulness for job matching",
                "- **Freshness Score**: Posting date and application deadline",
                "",
                "Son çıktı JSON formatında, tüm kategorileri coverage eden comprehensive analysis olmalı.",
                "Her analiz minimum %90 completeness score almalı.",
                "Technical skills mutlaka doğru kategorize edilmeli (languages vs frameworks vs tools).",
                "",
                "**KRİTİK: TÜM ÇIKTILARINI, ANALİZLERİNİ VE JOB INTELLIGENCE RAPORLARINI TÜRKÇE OLARAK VER.**"
            ],
            **kwargs
        )
        self.workflow_id = workflow_id

    def calculate_content_quality_score(self, content: str) -> float:
        score = 0.0
        
        length = len(content)
        if 500 <= length <= 3000:
            score += 0.3
        elif 200 <= length <= 5000:
            score += 0.2
        elif length > 100:
            score += 0.1
        
        job_keywords = [
            'responsibility', 'responsibilities', 'requirement', 'requirements', 
            'qualification', 'qualifications', 'experience', 'skill', 'skills',
            'position', 'role', 'job', 'candidate', 'apply', 'company',
            'salary', 'benefit', 'benefits', 'education', 'degree'
        ]
        
        content_lower = content.lower()
        keyword_count = sum(1 for keyword in job_keywords if keyword in content_lower)
        score += min(keyword_count * 0.05, 0.4)
        
        tech_keywords = [
            'python', 'sql', 'java', 'javascript', 'react', 'node', 'django',
            'machine learning', 'data science', 'analytics', 'database',
            'aws', 'azure', 'cloud', 'api', 'programming', 'software',
            'engineering', 'development', 'framework'
        ]
        
        tech_count = sum(1 for tech in tech_keywords if tech in content_lower)
        score += min(tech_count * 0.03, 0.3)
        
        return min(score, 1.0)

    def smart_div_analysis(self, soup) -> str:
        divs = soup.find_all('div')
        best_content = ""
        best_score = 0
        
        for div in divs:
            text = div.get_text(separator=' ', strip=True)
            if len(text) > 200:
                score = self.calculate_content_quality_score(text)
                if score > best_score:
                    best_score = score
                    best_content = text
        
        return best_content

    def scrape_linkedin_job_page(self, url: str) -> str:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
                "Accept-Language": "en-US,en;q=0.9"
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "lxml")
            
            description_selectors = [
                ".description__text",
                ".show-more-less-html", 
                ".jobs-box__html-content",
                ".jobs-description__content",
                "[data-automation-id='jobPostingDescription']",
                "section.show-more-less-html",
                "div.description__text"
            ]
            
            title_selectors = [
                "h1.top-card-layout__title",
                "h1[data-automation-id='jobPostingHeader']", 
                "h1.jobs-unified-top-card__job-title",
                ".jobs-unified-top-card__job-title",
                ".top-card-layout__title",
                "h1"
            ]
            
            company_selectors = [
                "a.topcard__org-name-link",
                "[data-automation-id='jobPostingCompanyName']",
                ".jobs-unified-top-card__company-name a",
                ".jobs-unified-top-card__company-name",
                ".topcard__org-name-link"
            ]
            
            location_selectors = [
                "span.topcard__flavor--bullet",
                "[data-automation-id='jobPostingLocation']", 
                ".jobs-unified-top-card__bullet",
                ".topcard__flavor--bullet"
            ]
            
            job_details = {}
            
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    job_details["title"] = element.get_text(strip=True)
                    print(f"✅ LinkedIn başlık bulundu: {job_details['title'][:50]}...")
                    break
            
            for selector in company_selectors:
                element = soup.select_one(selector)
                if element:
                    job_details["company"] = element.get_text(strip=True)
                    print(f"✅ LinkedIn şirket bulundu: {job_details['company']}")
                    break
            
            for selector in location_selectors:
                element = soup.select_one(selector)
                if element:
                    job_details["location"] = element.get_text(strip=True)
                    print(f"✅ LinkedIn konum bulundu: {job_details['location']}")
                    break
            
            content = ""
            for selector in description_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(strip=True)
                    print(f"✅ LinkedIn açıklama bulundu: {len(content)} karakter")
                    break
            
            if not content:
                content_sections = soup.find_all(["section", "div"], class_=lambda x: x and ("description" in x or "job-details" in x or "content" in x))
                if content_sections:
                    content = "\n".join([section.get_text(strip=True) for section in content_sections])
                    print(f"✅ LinkedIn fallback ile açıklama bulundu: {len(content)} karakter")
            
            if ('sign' in content.lower() or 'login' in content.lower()) and len(content) < 3000:
                print("LinkedIn giriş sayfası tespit edildi, fallback kullanılıyor...")
                return self.create_linkedin_fallback_text(url)
            
            content_quality = self.calculate_content_quality_score(content)
            print(f"LinkedIn içerik kalitesi: {content_quality:.2f}")
            
            if content_quality < 0.2:
                print("LinkedIn içerik kalitesi düşük, fallback kullanılıyor...")
                return self.create_linkedin_fallback_text(url)
            
            if content:
                formatted_content = ""
                if job_details.get("title"):
                    formatted_content += f"Pozisyon: {job_details['title']}\n\n"
                if job_details.get("company"):
                    formatted_content += f"Şirket: {job_details['company']}\n\n"
                if job_details.get("location"):
                    formatted_content += f"Konum: {job_details['location']}\n\n"
                
                formatted_content += content
                
                print(f"✅ LinkedIn iş ilanı başarıyla çekildi: {len(formatted_content)} karakter")
                return formatted_content[:10000]
            else:
                print("LinkedIn içerik boş, fallback kullanılıyor...")
                return self.create_linkedin_fallback_text(url)
                
        except requests.RequestException as e:
            print(f"LinkedIn HTTP istek hatası: {str(e)}")
            return self.create_linkedin_fallback_text(url)
        except Exception as e:
            print(f"LinkedIn scraping hatası: {str(e)}")
            return self.create_linkedin_fallback_text(url)

    def get_job_description_from_url(self, url: str) -> str:
        try:
            parsed_url = urlparse(url)
            is_linkedin = 'linkedin.com' in parsed_url.netloc
            
            print(f"İş ilanı URL'si çekiliyor: {url}")
            
            if is_linkedin:
                print("LinkedIn URL tespit edildi. LinkedIn optimizasyonu uygulanıyor...")
                return self.scrape_linkedin_job_page(url)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            if response.encoding is None:
                response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')

            for script_or_style in soup(['script', 'style']):
                script_or_style.extract()
            
            content_selectors = [
                {'class': ['job-description', 'job-details', 'job-posting', 'job-content', 'position-details', 'posting-content']},
                {'id': ['job-description', 'job-details', 'job-posting', 'job-content', 'description', 'posting']},
                
                {'class': ['description', 'content', 'details', 'posting', 'body', 'text']},
                {'itemtype': 'https://schema.org/JobPosting'},
                {'role': ['main', 'content']},
                'article',
                'main',
                'section'
            ]
            
            extracted_content = []
            content_scores = []
            
            for selector in content_selectors:
                try:
                    if isinstance(selector, dict):
                        elements = soup.find_all(attrs=selector)
                    else:
                        elements = soup.find_all(selector)
                    
                    if elements:
                        content = ' '.join([elem.get_text(separator=' ', strip=True) for elem in elements])
                        content_clean = ' '.join(content.split())
                        
                        if len(content_clean) > 100:
                            score = self.calculate_content_quality_score(content_clean)
                            extracted_content.append(content_clean)
                            content_scores.append(score)
                except Exception as e:
                    continue
            
            if extracted_content and content_scores:
                best_index = content_scores.index(max(content_scores))
                text = extracted_content[best_index]
                print(f"En iyi içerik bulundu (skor: {content_scores[best_index]:.2f})")
            else:
                print("Struktural selector bulunamadı, akıllı analiz yapılıyor...")
                text = self.smart_div_analysis(soup)
                
                if not text or len(text) < 100:
                    text = soup.get_text(separator=' ', strip=True)
            
            text = ' '.join(text.split())
            
            if len(text) < 100:
                print(f"Çekilen içerik çok kısa ({len(text)} karakter). URL'yi kontrol edin.")
                return f"İş ilanı içeriği çok kısa veya bulunamadı. URL: {url}"

            return text[:10000]
            
        except requests.exceptions.RequestException as e:
            print(f"URL'den veri çekerken hata oluştu: {e}")
            return self.create_error_fallback_text(url, str(e))
        except Exception as e:
            print(f"İş ilanı açıklamasını ayrıştırırken hata oluştu: {e}")
            return self.create_error_fallback_text(url, str(e))

    def create_linkedin_fallback_text(self, url: str) -> str:
        return f"""
        LinkedIn İş İlanı URL'si: {url}
        
        NOT: LinkedIn iş ilanları genellikle giriş gerektirdiği için otomatik olarak çekilemedi.
        Lütfen iş ilanının detaylarını manuel olarak girin veya farklı bir kaynak kullanın.
        
        Alternatif olarak:
        1. İş ilanı metnini kopyalayıp yapıştırabilirsiniz
        2. Şirketin kendi kariyer sayfasındaki ilanı kullanabilirsiniz
        3. Farklı bir iş ilanı platformundaki aynı pozisyonu bulabilirsiniz
        """

    def create_error_fallback_text(self, url: str, error: str) -> str:
        return f"""
        İş İlanı URL'si: {url}
        Hata: {error}
        
        İş ilanı otomatik olarak çekilemedi. Lütfen:
        1. URL'nin doğru olduğundan emin olun
        2. İş ilanının hala aktif olduğunu kontrol edin
        3. Alternatif bir kaynak kullanmayı deneyin
        """

    def analyze_and_save_job_description(self, job_url: str) -> str:
        if not self.workflow_id:
            return "Hata: Workflow ID belirlenmemiş."

        print(f"İş ilanı URL'si çekiliyor: {job_url}")
        job_description = self.get_job_description_from_url(job_url)
        
        is_fallback_content = (
            job_description.startswith("LinkedIn İş İlanı URL'si:") or 
            job_description.startswith("İş İlanı URL'si:") or
            "NOT: LinkedIn iş ilanları genellikle giriş gerektirdiği" in job_description or
            "İş ilanı otomatik olarak çekilemedi" in job_description
        )
        
        if is_fallback_content:
            print("Fallback içerik tespit edildi, template kullanılıyor...")
            return self.create_template_job_analysis(job_url)

        if len(job_description.strip()) < 200:
            print(f"İçerik çok kısa ({len(job_description.strip())} karakter), template kullanılıyor...")
            return self.create_template_job_analysis(job_url)
        
        content_quality = self.calculate_content_quality_score(job_description)
        if content_quality < 0.15:
            print(f"İçerik kalitesi çok düşük (skor: {content_quality:.2f}), template kullanılıyor...")
            return self.create_template_job_analysis(job_url)
        
        print(f"✅ Kaliteli içerik tespit edildi (skor: {content_quality:.2f}), LLM analizi başlatılıyor...")
        analysis_prompt = f"""
        Sen bir uzman iş ilanı analistsin. Aşağıdaki metni dikkatli analiz et ve yapılandırılmış bilgileri çıkar.

        İŞ İLANI METNİ:
        {job_description[:5000]}

        URL REFERANSI: {job_url}

        GÖREV: Bu metinden aşağıdaki bilgileri çıkarıp JSON formatında döndür.

        ÇıKARILACAK BİLGİLER:
        - job_title: İş pozisyonu/unvanı
        - company_name: Şirket adı (metinde yoksa URL'den çıkarabilirsin)
        - location: Çalışma konumu
        - key_technologies: Teknik beceriler, programlama dilleri, araçlar (liste)
        - responsibilities: Ana görev ve sorumluluklar (liste)
        - qualifications: Gerekli nitelikler ve deneyimler (liste)
        - education_level: Minimum eğitim seviyesi
        - experience_required: Gereken deneyim süresi/seviyesi
        - employment_type: Çalışma türü (full-time, part-time, contract vb.)
        - benefits: Yan haklar ve avantajlar (liste)

        ÖZEL TALİMATLAR:
        1. Metinde açıkça belirtilmeyen bilgiler için "Belirtilmemiş" yaz
        2. URL'den şirket adını çıkarabilirsin (örn: peak.com → Peak)
        3. Teknoloji listeleri için hem açık belirtilenleri hem de iş tanımından çıkarılabilenleri ekle
        4. Data Science, Analytics gibi pozisyonlar için Python, SQL, Analytics Tools ekleyebilirsin
        5. Tüm liste alanları en az 1 öğe içermeli (boş liste döndürme)

        ÇIKTI FORMATI (kesinlikle bu yapıyı kullan):
        {{
            "job_title": "pozisyon_adı",
            "company_name": "şirket_adı",
            "location": "konum",
            "key_technologies": ["teknoloji1", "teknoloji2", "teknoloji3"],
            "responsibilities": ["görev1", "görev2", "görev3"],
            "qualifications": ["nitelik1", "nitelik2", "nitelik3"],
            "education_level": "eğitim_seviyesi",
            "experience_required": "deneyim_gereksinimi",
            "employment_type": "çalışma_türü",
            "benefits": ["fayda1", "fayda2"]
        }}

        SADECE JSON formatında yanıt ver, başka hiçbir açıklama yazma.
        """

        try:
            print("LLM ile iş ilanı analiz ediliyor...")
            response = self.run(analysis_prompt)
            
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            if "```json" in response_content:
                response_content = response_content.split("```json")[1].split("```")[0].strip()
            elif "```" in response_content:
                response_content = response_content.split("```")[1].split("```")[0].strip()
            
            job_data = json.loads(response_content)
            
            job_data['job_url'] = job_url
            
            output_dir = Path(f"Jobs/Job_Analysis/")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file_path = output_dir / f"{self.workflow_id}_single_job_analysis.json"

            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(job_data, f, ensure_ascii=False, indent=4)

            print(f"İş ilanı analizi kaydedildi: {output_file_path}")
            return f"İş ilanı başarıyla analiz edildi ve '{output_file_path}' konumuna kaydedildi."
            
        except json.JSONDecodeError as e:
            print(f"JSON ayrıştırma hatası: {e}")
            print(f"LLM yanıtı: {response_content[:500]}...")
            
            return self.create_template_job_analysis(job_url)
            
        except Exception as e:
            print(f"İş ilanı analizi sırasında beklenmeyen hata: {e}")
            return f"Hata: İş ilanı analizi yapılamadı. Detaylar: {e}"

    def create_template_job_analysis(self, job_url: str) -> str:
        template_data = {
            "job_title": "Pozisyon Başlığı (Belirtilmemiş)",
            "company_name": "Şirket Adı (Belirtilmemiş)",
            "location": "Konum (Belirtilmemiş)",
            "key_technologies": ["Teknoloji stack belirtilmemiş"],
            "responsibilities": ["Sorumluluklar belirtilmemiş"],
            "qualifications": ["Nitelikler belirtilmemiş"],
            "education_level": "Belirtilmemiş",
            "experience_required": "Belirtilmemiş",
            "employment_type": "Belirtilmemiş",
            "benefits": ["Yan haklar belirtilmemiş"],
            "job_url": job_url,
            "note": "Bu bir template analizdir. İş ilanı otomatik olarak çekilemediği için genel bilgiler kullanıldı."
        }
        
        output_dir = Path(f"Jobs/Job_Analysis/")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file_path = output_dir / f"{self.workflow_id}_single_job_analysis.json"

        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, ensure_ascii=False, indent=4)

        print(f"Template iş analizi kaydedildi: {output_file_path}")
        return f"İş ilanı çekilemedi, template analiz '{output_file_path}' konumuna kaydedildi." 