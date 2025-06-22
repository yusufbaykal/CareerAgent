import requests
from bs4 import BeautifulSoup
from agno.tools import Toolkit
from agno.tools import tool


class SingleJobAnalysisToolkit(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @tool
    def get_job_description_from_url(self, url: str) -> str:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            for script_or_style in soup(['script', 'style']):
                script_or_style.extract()
            
            text = soup.get_text(separator=' ', strip=True)
            
            text = ' '.join(text.split())

            return text
        except requests.exceptions.RequestException as e:
            print(f"URL'den veri çekerken hata oluştu: {e}")
            return f"Error: Could not retrieve job description from {url}"
        except Exception as e:
            print(f"İş ilanı açıklamasını ayrıştırırken hata oluştu: {e}")
            return f"Error: Could not parse job description from {url}" 