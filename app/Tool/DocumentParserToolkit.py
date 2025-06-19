from agno.tools import Toolkit
import PyPDF2
import os
import json
from Tool.ContentCache import cache
from agno.utils.log import logger


class DocumentParserToolkit(Toolkit):
    def __init__(self):
        super().__init__(name="document_parser")
        self.register(self.parse_document)
        self.register(self.extract_from_pdf)
        self.register(self.extract_from_text)
        
    def parse_document(self, file_path: str) -> str:
        try:
            if not os.path.exists(file_path):
                return json.dumps({"error": f"Dosya bulunamadı: {file_path}"})
                
            cache_key = f"doc_{file_path}_{os.path.getmtime(file_path)}"
            cached = cache.get(cache_key)
            if cached:
                logger.info(f"Önbellekten döndürülüyor: {file_path}")
                return cached
                
            file_ext = os.path.splitext(file_path)[1].lower()
            
            content = ""
            if file_ext == ".pdf":
                content = self.extract_from_pdf(file_path)
            elif file_ext in [".txt", ".text", ".md"]:
                content = self.extract_from_text(file_path)
            else:
                return json.dumps({"error": f"Desteklenmeyen dosya türü: {file_ext}. Desteklenen türler: .pdf, .txt, .text, .md"})
                
            if content and not content.startswith('{"error"'):
                cache.set(cache_key, content)
                
            return content
            
        except Exception as e:
            logger.error(f"Belge ayrıştırma hatası: {str(e)}")
            return json.dumps({"error": f"Belge ayrıştırma hatası: {str(e)}"})
            
    def extract_from_pdf(self, file_path: str) -> str:
        try:
            if not os.path.exists(file_path):
                return json.dumps({"error": f"PDF dosyası bulunamadı: {file_path}"})
            
            text = ""
            with open(file_path, "rb") as file:
                try:
                    reader = PyPDF2.PdfReader(file)
                    for page_num in range(len(reader.pages)):
                        try:
                            page_text = reader.pages[page_num].extract_text()
                            if page_text.strip():
                                text += page_text + "\n"
                        except Exception as e:
                            logger.warning(f"Sayfa {page_num + 1} okunamadı: {str(e)}")
                            continue
                except Exception as e:
                    logger.error(f"PDF reader hatası: {str(e)}")
                    return json.dumps({"error": f"PDF okuma hatası: {str(e)}"})
            
            if not text.strip():
                return json.dumps({"error": "PDF'den metin çıkarılamadı. Dosya görüntü tabanlı olabilir."})
                
            return text.strip()
            
        except ImportError:
            error_msg = "PyPDF2 kütüphanesi yüklü değil. 'pip install PyPDF2' komutu ile yükleyebilirsiniz."
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
        except Exception as e:
            logger.error(f"PDF okuma hatası: {str(e)}")
            return json.dumps({"error": f"PDF okuma hatası: {str(e)}"})
    
    def extract_from_text(self, file_path: str) -> str:
        try:
            if not os.path.exists(file_path):
                return json.dumps({"error": f"Metin dosyası bulunamadı: {file_path}"})
            
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
            except UnicodeDecodeError:
                logger.warning(f"UTF-8 okuma başarısız, latin-1 deneniyor: {file_path}")
                try:
                    with open(file_path, "r", encoding="latin-1") as file:
                        content = file.read()
                except Exception as e:
                    logger.error(f"Encoding hatası: {str(e)}")
                    return json.dumps({"error": f"Dosya encoding hatası: {str(e)}"})
            
            if not content.strip():
                return json.dumps({"error": "Metin dosyası boş."})
                
            return content.strip()
            
        except Exception as e:
            logger.error(f"Metin dosyası okuma hatası: {str(e)}")
            return json.dumps({"error": f"Metin dosyası okuma hatası: {str(e)}"})