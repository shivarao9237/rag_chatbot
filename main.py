# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile, os
from src.search import RAGSearch

app = FastAPI(title="RAG Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_search: RAGSearch | None = None  # global in-memory instance

@app.post("/upload")
async def upload_pdfs(files: list[UploadFile] = File(...)):
    global rag_search
    saved_paths = []
    for f in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir="/tmp") as tmp:
            tmp.write(await f.read())
            saved_paths.append(tmp.name)
    rag_search = RAGSearch(persist_dir="/tmp/faiss_store", data_paths=saved_paths)
    return {"message": f"{len(saved_paths)} PDF(s) processed successfully."}

class QuestionRequest(BaseModel):
    question: str
    top_k: int = 3

@app.post("/ask")
async def ask_question(body: QuestionRequest):
    if not rag_search:
        raise HTTPException(status_code=400, detail="No documents uploaded yet.")
    answer = rag_search.search_and_summarize(body.question, top_k=body.top_k)
    return {"answer": answer}

@app.get("/health")
def health():
    return {"status": "ok", "docs_loaded": rag_search is not None}