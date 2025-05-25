from pathlib import Path
import os


class DocumentManager:
    def __init__(self):
        self.current_doc = None
        self.loaded_docs = {}

    def set_current(self, doc_name: str):
        self.current_doc = doc_name

    def get_current(self) -> str:
        return self.current_doc


# Инициализация менеджера
doc_manager = DocumentManager()

# Пути как объекты Path
BASE_DIR = Path(__file__).parent.resolve()
MODELS_DIR = BASE_DIR / "models"
MODEL_NAME = "Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"

# Создание директорий
for directory in [
    BASE_DIR / "data" / "documents",
    BASE_DIR / "data" / "chroma_db",
    MODELS_DIR
]:
    directory.mkdir(parents=True, exist_ok=True)

# Конфигурационные параметры (возвращаем как строки)
BOT_TOKEN = "8114706168:AAFT02csswRXmaU1_-h3W96m97RGru32BDk"
DOCUMENTS_DIR = str(BASE_DIR / "data" / "documents")
CHROMA_DB_DIR = str(BASE_DIR / "data" / "chroma_db")
MODEL_PATH = str(MODELS_DIR / MODEL_NAME)