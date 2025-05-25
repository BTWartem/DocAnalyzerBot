from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from config import doc_manager, CHROMA_DB_DIR
import os


def create_vector_db(text: str, db_name: str) -> None:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_text(text)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    Chroma.from_texts(
        chunks,
        embeddings,
        persist_directory=os.path.join(CHROMA_DB_DIR, db_name)
    )
    doc_manager.loaded_docs[db_name] = True


def load_vector_db(db_name: str):
    if db_name not in doc_manager.loaded_docs:
        raise ValueError(f"Документ {db_name} не загружен")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return Chroma(
        persist_directory=os.path.join(CHROMA_DB_DIR, db_name),
        embedding_function=embeddings
    )