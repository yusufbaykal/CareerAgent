from agno.tools import Toolkit
import os
import json
from datetime import datetime
from agno.utils.log import logger
from typing import Any

class FileToolkit(Toolkit):
    def __init__(self):
        super().__init__(name="file_tools")
        self.register(self.save_json)
        self.register(self.save_text)
        self.register(self.list_directory)
        self.register(self.read_json)
        
    def save_json(self, data: Any, file_path: str) -> str:
        try:
            normalized_path = file_path.replace('\\', '/')
            full_path = os.path.abspath(normalized_path)
            
            directory = os.path.dirname(full_path)
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Dizin oluşturuldu: {directory}")
            
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            if os.path.exists(full_path):
                file_size = os.path.getsize(full_path)
                logger.info(f"✅ JSON verisi başarıyla kaydedildi: {full_path} ({file_size} bytes)")
                return f"✅ BAŞARILI: JSON verisi '{full_path}' dosyasına kaydedildi. ({file_size} bytes)"
            else:
                raise Exception("Dosya yazıldı ama teyit edilemedi")
                
        except Exception as e:
            error_msg = f"Dosya kaydetme hatası: {str(e)}"
            logger.error(error_msg)
            
            try:
                backup_path = full_path.replace('.json', '_backup.json')
                with open(backup_path, 'w', encoding='utf-8-sig') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info(f"Backup dosya oluşturuldu: {backup_path}")
                return f"⚠️ Backup olarak kaydedildi: {backup_path}"
            except:
                pass
                
            return f"❌ HATA: {error_msg}"
    
    def save_text(self, text: str, file_path: str) -> str:
        try:
            full_path = os.path.abspath(file_path)
            
            directory = os.path.dirname(full_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"Dizin oluşturuldu: {directory}")
                
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(text)
                
            logger.info(f"Metin başarıyla kaydedildi: {full_path}")
            return f"Başarılı: Metin '{full_path}' dosyasına kaydedildi."
            
        except Exception as e:
            error_msg = f"Dosya kaydetme hatası: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
    
    def list_directory(self, dir_path: str = ".") -> str:
        try:
            full_path = os.path.abspath(dir_path)
            
            if not os.path.exists(full_path):
                return json.dumps({"error": f"Dizin bulunamadı: {full_path}"})
                
            if not os.path.isdir(full_path):
                return json.dumps({"error": f"Belirtilen yol bir dizin değil: {full_path}"})
                
            files = []
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                item_type = "directory" if os.path.isdir(item_path) else "file"
                item_size = os.path.getsize(item_path) if item_type == "file" else None
                item_modified = datetime.fromtimestamp(os.path.getmtime(item_path)).strftime("%Y-%m-%d %H:%M:%S")
                
                files.append({
                    "name": item,
                    "type": item_type,
                    "size": item_size,
                    "modified": item_modified
                })
                
            return json.dumps({"path": full_path, "items": files}, ensure_ascii=False)
            
        except Exception as e:
            error_msg = f"Dizin listeleme hatası: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
        
    def read_json(self, file_path: str) -> str:
        try:
            full_path = os.path.abspath(file_path)
            if not os.path.exists(full_path):
                return json.dumps({"error": f"Dosya bulunamadı: {full_path}"})
                
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            logger.info(f"JSON dosyası başarıyla okundu: {full_path}")
            return json.dumps(data, ensure_ascii=False)
            
        except Exception as e:
            error_msg = f"Dosya okuma hatası: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})