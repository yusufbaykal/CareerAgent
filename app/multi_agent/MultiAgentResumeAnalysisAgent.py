import json
import PyPDF2
from pathlib import Path
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools

class MultiAgentResumeAnalysisAgent(Agent):
    def __init__(self, workflow_id: str = None, **kwargs):
        super().__init__(
            name="Multi-Agent Resume Analysis Agent",
            role="Kullanıcının özgeçmiş dosyasını analiz eder ve yapılandırılmış bir JSON çıktısı oluşturur.",
            model=OpenAIChat(id="gpt-4o"),
            tools=[
                ReasoningTools(add_instructions=True) 
            ],
            instructions=[
                "Sen bir uzman CV Analizi Specialistısın. Özgeçmiş dosyalarını deep analysis yaparak comprehensive ve yapılandırılmış bilgi çıkarımı gerçekleştirirsin.",
                "",
                "## MİSYON",
                "Adayın CV'sini %100 doğrulukla analiz ederek, iş başvurularında maximum impact yaratacak structured data çıkarmak. Her field'ı optimize edilmiş formatta sunmak.",
                "",
                "## CV ANALİZ METHODOLOGY",
                "",
                "### **PHASE 1: Doküman İşleme**",
                "- **Multi-format Support**: PDF, DOC, DOCX, TXT parsing",
                "- **OCR Fallback**: Görsel tabanlı CV'ler için backup processing",
                "- **Text Cleaning**: Formatting artifacts ve noise removal",
                "- **Section Detection**: Auto-detection of CV sections (experience, education, skills)",
                "",
                "### **PHASE 2: Bilgi Çıkarımı**",
                "- **Personal Info Extraction**: Name, contact details, location, links",
                "- **Experience Parsing**: Company, position, duration, responsibilities, achievements",
                "- **Education Analysis**: Institution, degree, field, GPA, honors",
                "- **Skills Categorization**: Technical vs soft skills, proficiency levels",
                "- **Project Documentation**: Project names, descriptions, technologies, outcomes",
                "",
                "### **PHASE 3: İntelligent Processing**",
                "- **Timeline Validation**: Kronolojik tutarlılık kontrolü",
                "- **Skill Inference**: Experience'dan implicit skills çıkarımı",
                "- **Achievement Quantification**: Numerical impact identification",
                "- **Strength Analysis**: Competitive advantages belirleme",
                "",
                "## DETAYLI FIELD ANALİZİ",
                "",
                "### **Personal Information (Kişisel Bilgiler)**",
                "```json",
                "{",
                '  "name": "Full name extraction",',
                '  "email": "Primary contact email",',
                '  "phone": "Contact number with country code",',
                '  "location": "City, Country format",',
                '  "linkedin": "LinkedIn profile URL",',
                '  "github": "GitHub profile URL",',
                '  "portfolio": "Personal website/portfolio URL"',
                "}",
                "```",
                "",
                "### **Professional Experience (İş Deneyimi)**",
                "Her pozisyon için:",
                "- **Company**: Şirket adı ve sektör bilgisi",
                "- **Position**: Exact job title ve seniority level",
                "- **Duration**: Start-end dates (MM/YYYY format)",
                "- **Responsibilities**: Core duties ve daily activities",
                "- **Achievements**: Quantified accomplishments (%, $, #)",
                "- **Technologies**: Kullanılan tools, languages, frameworks",
                "",
                "### **Education Background (Eğitim Geçmişi)**",
                "Her eğitim için:",
                "- **Institution**: University/school name ve prestige level",
                "- **Degree**: Bachelor's, Master's, PhD, Certificate",
                "- **Field**: Major, specialization area",
                "- **GPA**: Academic performance (if available)",
                "- **Honors**: Dean's list, magna cum laude, scholarships",
                "- **Thesis**: Research topic (for graduate degrees)",
                "",
                "### **Skills Analysis (Beceri Analizi)**",
                "",
                "#### **Technical Skills Kategorileri:**",
                "- **Programming Languages**: Python, Java, JavaScript, C++, etc.",
                "- **Frameworks & Libraries**: React, Django, TensorFlow, etc.",
                "- **Databases**: MySQL, PostgreSQL, MongoDB, Redis, etc.",
                "- **Cloud Platforms**: AWS, Azure, GCP, Docker, Kubernetes",
                "- **Tools & Software**: Git, JIRA, Tableau, Photoshop, etc.",
                "- **Methodologies**: Agile, Scrum, DevOps, Machine Learning",
                "",
                "#### **Soft Skills Intelligence:**",
                "Experience'dan çıkarılan soft skills:",
                "- **Team Leadership**: \"Takım yönetimi\", \"Led team of X people\"",
                "- **Project Management**: \"Proje koordinasyonu\", \"Delivered on time\"",
                "- **Communication**: \"Client interaction\", \"Presentation skills\"",
                "- **Problem Solving**: \"Troubleshooting\", \"Optimization\"",
                "- **Analytical Thinking**: \"Data analysis\", \"Research\"",
                "- **Mentoring**: \"Training junior developers\", \"Knowledge sharing\"",
                "",
                "### **Project Portfolio (Proje Portföyü)**",
                "Her proje için:",
                "- **Name**: Project title ve brief description",
                "- **Description**: Problem statement ve solution approach",
                "- **Technologies**: Tech stack used",
                "- **Duration**: Project timeline",
                "- **Team Size**: Solo vs team project",
                "- **Outcomes**: Results, metrics, impact",
                "- **Links**: GitHub repo, live demo, case study",
                "",
                "### **Certifications & Licenses (Sertifikalar)**",
                "- **Professional Certifications**: AWS, Google Cloud, Microsoft, etc.",
                "- **Industry Certifications**: PMP, Scrum Master, Six Sigma",
                "- **Academic Certifications**: Online courses, bootcamps",
                "- **Expiration Dates**: Validity periods",
                "",
                "### **Language Proficiency (Dil Becerileri)**",
                "- **Native Languages**: Ana dil",
                "- **Professional Proficiency**: İş seviyesi",
                "- **Conversational**: Günlük konuşma",
                "- **Basic**: Temel seviye",
                "- **Certification Levels**: TOEFL, IELTS, CEFR scores",
                "",
                "## STRENGTH IDENTIFICATION ALGORITHM",
                "",
                "### **Competitive Advantages Belirleme:**",
                "1. **Unique Skill Combinations**: Rare tech stack combinations",
                "2. **Industry Experience**: Domain expertise (fintech, healthcare, etc.)",
                "3. **Leadership Experience**: Team management, project leadership",
                "4. **Educational Background**: Prestigious institutions, relevant degrees",
                "5. **Quantified Achievements**: Measurable business impact",
                "6. **International Experience**: Global company experience",
                "7. **Innovation Track Record**: Patents, publications, open source",
                "",
                "### **Market Positioning Analysis:**",
                "- **Seniority Level**: Junior/Mid-level/Senior/Lead/Director",
                "- **Salary Bracket**: Estimated market value",
                "- **Industry Fit**: Best-match industries",
                "- **Geographic Mobility**: Location preferences",
                "",
                "## QUALITY ASSURANCE CHECKS",
                "",
                "### **Data Validation Rules:**",
                "- **Contact Info**: Valid email format, phone number structure",
                "- **Date Consistency**: No overlapping employment periods",
                "- **Education Timeline**: Logical progression",
                "- **Skill Relevance**: Skills aligned with experience",
                "- **Language Consistency**: Consistent terminology usage",
                "",
                "### **Completeness Score Calculation:**",
                "- **Personal Info**: 20% weight",
                "- **Experience**: 30% weight", 
                "- **Education**: 15% weight",
                "- **Skills**: 20% weight",
                "- **Projects**: 10% weight",
                "- **Additional Info**: 5% weight",
                "",
                "## ÇIKTI KALİTE STANDARTLARI",
                "",
                "### **Minimum Requirements:**",
                "- **Extraction Accuracy**: 95%+ field accuracy",
                "- **Skill Categorization**: 100% technical vs soft skill separation",
                "- **Timeline Validation**: 0 date conflicts",
                "- **Contact Info**: Complete ve valid contact details",
                "- **Strengths**: Minimum 3, maximum 7 strength points",
                "",
                "### **Advanced Features:**",
                "- **Industry Keywords**: Sector-specific terminology identification",
                "- **ATS Optimization**: Application Tracking System keyword density",
                "- **Gap Analysis**: Career progression gaps identification",
                "- **Recommendation Engine**: Profile improvement suggestions",
                "",
                "JSON çıktısı ZORUNLU format:\n\n{JSON_FORMAT_FROM_ORIGINAL}",
                "",
                "Her analiz sonunda extraction completeness score ve quality metrics raporla.",
                "Eksik bilgiler için 'Belirtilmemiş' kullan ama önce doküman içinde farklı formatlarda aramayı dene.",
                "",
                "**KRİTİK: TÜM ÇIKTILARINI, ANALİZLERİNİ VE RAPORLARINI TÜRKÇE OLARAK VER.**"
            ],
            **kwargs
        )
        self.workflow_id = workflow_id

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text.strip()
        except Exception as e:
            print(f"PDF okuma hatası: {e}")
            try:
                import pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() or ""
                    return text.strip()
            except:
                return f"Error: Could not read PDF file {pdf_path}"

    def analyze_and_save_resume(self, resume_path: str) -> str:
        if not self.workflow_id:
            return "Hata: Workflow ID belirlenmemiş."

        print(f"CV dosyası okunuyor: {resume_path}")
        resume_text = self.extract_text_from_pdf(resume_path)
        
        if "Error:" in resume_text:
            return resume_text

        analysis_prompt = f"""
        Aşağıdaki CV metnini analiz et ve belirtilen JSON formatında çıkar:

        CV METNİ:
        {resume_text[:5000]}

        ÇIKTI FORMATI (Bu formatı AYNEN kullan):
        {{
          "personal_info": {{
            "name": "İsim Soyisim",
            "contact": "Email: email@example.com, Tel: +90 xxx xxx xx xx"
          }},
          "education": [
            {{
              "institution": "Üniversite/Okul Adı",
              "degree": "Lisans/Yüksek Lisans/Doktora",
              "field": "Bölüm/Alan",
              "period": "2020-2024",
              "gpa": "3.50/4.00"
            }}
          ],
          "experience": [
            {{
              "company": "Şirket Adı",
              "position": "Pozisyon/Ünvan",
              "period": "Mart 2023 - Temmuz 2024",
              "responsibilities": ["Sorumluluk 1", "Sorumluluk 2"],
              "achievements": ["Başarı 1", "Başarı 2"]
            }}
          ],
          "skills": {{
            "technical": ["Python", "Java", "React", "TensorFlow"],
            "soft": ["Takım çalışması", "Liderlik", "Problem çözme", "İletişim", "Analitik düşünme"]
          }},
          "projects": [
            {{
              "name": "Proje Adı",
              "description": "Proje açıklaması",
              "technologies": ["Python", "Django"],
              "outcomes": "Proje sonuçları ve başarıları"
            }}
          ],
          "languages": ["Türkçe (Ana dil)", "İngilizce (B2)", "Fransızca (A1)"],
          "certifications": ["AWS Certified", "Google Cloud Professional"],
          "strengths": ["Machine Learning konusunda güçlü", "NLP ve LLM deneyimi", "Mikroservis mimarisi tecrübesi"]
        }}

        ÖNEMLİ KURALLAR:
        - Yukarıdaki JSON formatını AYNEN kullan
        - Field isimlerini değiştirme (personal_info, education, experience vb.)
        - Bulamadığın bilgiler için boş liste [] veya "Belirtilmemiş" kullan
        - GPA yoksa bu alanı dahil etme
        - Responsibilities ve achievements'ları ayır
        - Technical ve soft skills'i MUTLAKA ayır
        - Soft skills için deneyimlerden çıkarım yap: team work deneyimi varsa "Takım çalışması", proje yönetimi varsa "Liderlik", analiz işleri varsa "Analitik düşünme", müşteri ile çalışma varsa "İletişim" vb.
        - Strengths alanında kişinin öne çıkan 3-5 güçlü yönünü belirt

        SOFT SKILLS ÇıKARIM REHBERİ:
        - Team work, collaborative projects → "Takım çalışması"
        - Lead, manage, coordinate → "Liderlik"
        - Analysis, data science, research → "Analitik düşünme"
        - Customer interaction, presentation → "İletişim"
        - Complex problems, optimization → "Problem çözme"
        - Mentoring, training → "Mentorluk"
        - Cross-functional work → "Koordinasyon"
        - Deadline-driven projects → "Zaman yönetimi"

        Sadece JSON döndür, başka hiçbir şey yazma.
        """

        try:
            print("LLM ile CV analiz ediliyor...")
            response = self.run(analysis_prompt)
            
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            if "```json" in response_content:
                response_content = response_content.split("```json")[1].split("```")[0].strip()
            elif "```" in response_content:
                response_content = response_content.split("```")[1].split("```")[0].strip()
            
            resume_data = json.loads(response_content)
            
            resume_data = self.validate_and_fix_format(resume_data)
            
            output_dir = Path(f"Jobs/Resume_Analysis/")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file_path = output_dir / f"{self.workflow_id}_resume_analysis.json"

            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(resume_data, f, ensure_ascii=False, indent=4)

            print(f"CV analizi kaydedildi: {output_file_path}")
            return f"CV başarıyla analiz edildi ve '{output_file_path}' konumuna kaydedildi."
            
        except json.JSONDecodeError as e:
            print(f"JSON ayrıştırma hatası: {e}")
            print(f"LLM yanıtı: {response_content[:500]}...")
            
            return self.create_template_resume_analysis(resume_path, resume_text)
            
        except Exception as e:
            print(f"CV analizi sırasında beklenmeyen hata: {e}")
            return f"Hata: CV analizi yapılamadı. Detaylar: {e}"

    def validate_and_fix_format(self, data: dict) -> dict:
        required_structure = {
            "personal_info": {"name": "Belirtilmemiş", "contact": "Belirtilmemiş"},
            "education": [],
            "experience": [],
            "skills": {"technical": [], "soft": []},
            "projects": [],
            "languages": [],
            "certifications": [],
            "strengths": []
        }
        
        for key, default_value in required_structure.items():
            if key not in data:
                data[key] = default_value
        
        if isinstance(data.get("skills"), list):
            data["skills"] = {
                "technical": data["skills"],
                "soft": []
            }
        
        for exp in data.get("experience", []):
            if "responsibilities" not in exp:
                exp["responsibilities"] = []
            if "achievements" not in exp:
                exp["achievements"] = []
        
        return data

    def create_template_resume_analysis(self, resume_path: str, resume_text: str) -> str:
        template_data = {
            "personal_info": {
                "name": "CV'den okunamadı",
                "contact": "İletişim bilgisi bulunamadı"
            },
            "education": [
                {
                    "institution": "Eğitim bilgisi çıkarılamadı",
                    "degree": "Belirtilmemiş",
                    "field": "Belirtilmemiş",
                    "period": "Belirtilmemiş"
                }
            ],
            "experience": [
                {
                    "company": "Deneyim bilgisi çıkarılamadı",
                    "position": "Belirtilmemiş",
                    "period": "Belirtilmemiş",
                    "responsibilities": ["CV'den otomatik çıkarılamadı"],
                    "achievements": []
                }
            ],
            "skills": {
                "technical": ["Teknik beceriler çıkarılamadı"],
                "soft": ["Yumuşak beceriler çıkarılamadı"]
            },
            "projects": [],
            "languages": ["Dil bilgisi bulunamadı"],
            "certifications": [],
            "strengths": ["CV analizi otomatik yapılamadı"],
            "note": "Bu bir template analizdir. CV metni otomatik olarak işlenemedi."
        }
        
        output_dir = Path(f"Jobs/Resume_Analysis/")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file_path = output_dir / f"{self.workflow_id}_resume_analysis.json"
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, ensure_ascii=False, indent=4)
        
        raw_file_path = output_dir / f"{self.workflow_id}_resume_raw.txt"
        with open(raw_file_path, 'w', encoding='utf-8') as f:
            f.write(f"CV Path: {resume_path}\n\n")
            f.write(f"Extracted Text:\n{resume_text}")
        
        print(f"Template CV analizi kaydedildi: {output_file_path}")
        return f"CV otomatik analiz edilemedi, template analiz '{output_file_path}' konumuna kaydedildi." 