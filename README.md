# 🚀 CareerAgent: AI‑Powered Career Assistant

CareerAgent is an advanced, agent-based system built to accelerate your career progression by automating job search and application tasks. It combines distributed agent architecture with LLM-powered insights to transform unstructured career data into actionable intelligence.
---

### LinkedIn Job Search Agent
Autonomous web scraping of LinkedIn listings using parameterized searches.  
Semantic filtering by technology, seniority, domain, and relevance.

### Resume Analysis Agent
Multi-format parsing (PDF, DOCX, TXT) to extract structured candidate information.  
NLP-powered skill extraction, experience categorization, and ATS compatibility analysis.

### Job Analysis Agent
Multi-source job description parsing with entity recognition.  
Extracts structured metadata: requirements, responsibilities, company attributes.  
Domain-specific classification and hierarchical skill mapping.

### Job Compatibility Engine
Vector-based similarity scoring to evaluate candidate–job fit.  
Weighted metrics across various dimensions.  
Identifies skill gaps and provides targeted upskilling recommendations.

### Cover Letter Generator
Context-aware automatic cover letter creation tailored to job specs.  
Customizable templates that dynamically emphasize your top qualifications based on compatibility analysis.

### Multi-Agent Orchestration
Fully operational asynchronous, parallel task execution with state management.  
Complete workflow automation from job URL and CV to final cover letter generation.  
Intelligent task prioritization, inter-agent communication, and automated error handling.

### Multi-Agent Workflow

The application includes a comprehensive Multi-Agent System that can:

1. **Analyze job URLs** - Extract and parse job requirements
2. **Process CVs** - Analyze candidate qualifications and experience  
3. **Calculate compatibility** - Generate detailed job-candidate fit scores
4. **Create cover letters** - Generate personalized application letters
5. **Export results** - Save all outputs in structured JSON and text formats
---

## 🛠️ Technology Stack

| Category          | Technologies                                       |
| ----------------- | -------------------------------------------------- |
| **Framework**     | Streamlit                                          |
| **AI & Agents**   | AgnoAgent, OpenAI GPT-4                           |
| **Multi-Agent**   | Asynchronous task orchestration, State management |
| **Web Scraping**  | BeautifulSoup4, Requests, LinkedIn Jobs API       |
| **Doc Processing**| PyPDF2, python-docx, Multi-format parsing         |
| **Data & Core**   | Python 3.10+, JSON, Pathlib, UUID, Dotenv        |

---

## 📦 Installation

A working Python 3.10+ environment and an OpenAI API key are required.

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd CareerAgent
    ```

2.  **Install dependencies:**
    *We recommend using `uv` for fast dependency management.*
    ```bash
    # Install uv if you haven't already
    pip install uv
    # Sync dependencies
    uv sync
    ```
    *Alternatively, use pip:*
    ```bash
    pip install -e .
    ```

---

## 🚀 Usage

### Launch the Streamlit Application

Once installed, run the main application from the project root:

```bash
# Using uv
uv run streamlit run app/streamlit_app.py

# Or with standard streamlit
streamlit run app/streamlit_app.py
```

Navigate to the local URL provided by Streamlit in your browser to start using the agents.


### CLI Usage *(Coming Soon)*

A command-line interface for advanced scripting and automation is under development.

```bash
career-agent --help
```

---

## 📁 Project Structure

The repository is organized to separate the application logic, agent toolkits, and user-generated data.

```
CareerAgent/
├── app/                        
│   ├── streamlit_app.py       
│   ├── *_agent.py              
│   ├── multi_agent/            
│   │   ├── CareerAgentTeamCoordinator.py  
│   │   ├── MultiAgentCoverLetterAgent.py  
│   │   ├── MultiAgentJobCompatibilityAgent.py  
│   │   ├── MultiAgentResumeAnalysisAgent.py   
│   │   └── SingleJobAnalysisAgent.py          
│   ├── Tool/                    
│   │   ├── ContentCache.py    
│   │   ├── CoverLetterToolkit.py 
│   │   ├── DocumentParserToolkit.py 
│   │   ├── FileToolkit.py     
│   │   ├── JobAnalysisToolkit.py
│   │   ├── JobCompatibilityToolkit.py 
│   │   ├── LinkedInJobsToolkit.py 
│   │   ├── ResumeAnalysisToolkit.py
│   │   ├── SingleJobAnalysisToolkit.py
│   │   └── WebScraperToolkit.py
│   └── ui/                     
│       ├── agent_manager.py     
│       └── streamlit_*_tab.py   
├── Jobs/                       
│   ├── Cover_Letters/          
│   ├── Job_Analysis/           
│   ├── Job_Compatibility/      
│   ├── Job_Results/            
│   ├── Resume_Analysis/         
│   └── Resumes/              
├── .gitignore                
├── LICENSE                      
├── pyproject.toml               
├── README.md                    
└── uv.lock                    
```

---

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/badge/python-3.10+-informational.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Streamlit-ff4b4b.svg)](https://streamlit.io/)
