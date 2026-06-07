import os
from dotenv import load_dotenv
from src.vectorstore import FaissVectorStore
from src.data_loader import load_all_documents
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader

load_dotenv()

class RAGSearch:
    def __init__(self, persist_dir: str = "/tmp/faiss_store",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 llm_model: str = "llama-3.3-70b-versatile",
                 data_paths: list = None):

        os.makedirs(persist_dir, exist_ok=True)
        self.vectorstore = FaissVectorStore(persist_dir, embedding_model)

        faiss_path = os.path.join(persist_dir, "faiss.index")
        meta_path = os.path.join(persist_dir, "metadata.pkl")

        if not (os.path.exists(faiss_path) and os.path.exists(meta_path)):
            # Load from provided file paths directly
            docs = []
            if data_paths:
                for path in data_paths:
                    try:
                        loader = PyPDFLoader(path)
                        docs.extend(loader.load())
                        print(f"[INFO] Loaded: {path}")
                    except Exception as e:
                        print(f"[ERROR] {path}: {e}")
            if docs:
                self.vectorstore.build_from_documents(docs)
            else:
                print("[WARNING] No documents loaded")
        else:
            self.vectorstore.load()

        groq_api_key = os.getenv("GROQ_API_KEY")
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name=llm_model
        )
        print(f"[INFO] Groq LLM initialized: {llm_model}")

    def search_and_summarize(self, query: str, top_k: int = 5) -> str:
        results = self.vectorstore.query(query, top_k=top_k)
        texts = [r["metadata"].get("text", "") for r in results if r["metadata"]]
        context = "\n\n".join(texts)
        if not context:
            return "No relevant documents found."
        prompt = f"""You are a helpful assistant. Answer the question based ONLY on the context below.
If the answer is not in the context, say "I couldn't find this in the document."

Context: {context}

Question: {query}

Answer:"""
        response = self.llm.invoke([prompt])
        return response.content