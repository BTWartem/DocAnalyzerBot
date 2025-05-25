from llama_cpp import Llama
from config import MODEL_PATH
import re
import os  # Добавляем импорт

# Конвертируем Path в строку перед использованием
model_path_str = str(MODEL_PATH) if hasattr(MODEL_PATH, '__str__') else MODEL_PATH

llm = Llama(
    model_path=model_path_str,  # Используем строковый путь
    n_ctx=2048,
    n_threads=4,
    n_gpu_layers=0,
    verbose=False
)


def generate_answer(question: str, context: str) -> str:
    prompt = f"""<|start_header_id|>system<|end_header_id|>
    Ты — русскоязычный ассистент для анализа документов. Отвечай ТОЛЬКО на русском языке.
    Контекст: {context}
    <|eot_id|>
    <|start_header_id|>user<|end_header_id|>
    Вопрос: {question}
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>"""

    output = llm(
        prompt,
        max_tokens=300,
        temperature=0.1,
        stop=["<|eot_id|>"]
    )
    return clean_response(output["choices"][0]["text"])


def clean_response(text: str) -> str:
    text = re.sub(r'(assistant|please|sorry|\n\s*)+', '', text, flags=re.IGNORECASE)
    return text.strip()