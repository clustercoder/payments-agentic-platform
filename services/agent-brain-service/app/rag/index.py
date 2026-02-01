from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from app.rag.loader import load_docs

def build_index():
    docs = load_docs()
    # Uses OPENAI_API_KEY from environment variables automatically
    embeddings = OpenAIEmbeddings()
    return FAISS.from_documents(docs, embeddings)