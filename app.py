# app.py
import streamlit as st
import os
from src.data_loader import load_all_documents
from src.vectorstore import FaissVectorStore
from src.search import RAGSearch

st.set_page_config(page_title="RAG Chatbot", page_icon="📄")
st.title("📄 Chat with your Documents")

# Session state
if "rag_search" not in st.session_state:
    st.session_state.rag_search = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar — upload PDFs
with st.sidebar:
    st.header("Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload PDFs", type="pdf", accept_multiple_files=True
    )
    if uploaded_files and st.button("Process", type="primary"):
        with st.spinner("Processing PDFs..."):
            # Save files to data/ folder
            os.makedirs("data", exist_ok=True)
            for f in uploaded_files:
                with open(f"data/{f.name}", "wb") as out:
                    out.write(f.read())
            # Build RAG pipeline
            st.session_state.rag_search = RAGSearch()
            st.session_state.chat_history = []
        st.success("Ready! Ask your questions.")

# Main chat area
if not st.session_state.rag_search:
    st.info("👈 Upload PDFs in the sidebar to get started")
else:
    # Show chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Question input
    question = st.chat_input("Ask a question about your documents...")
    if question:
        st.session_state.chat_history.append(
            {"role": "user", "content": question}
        )
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = st.session_state.rag_search.search_and_summarize(
                    question, top_k=3
                )
                st.write(answer)
        st.session_state.chat_history.append(
            {"role": "assistant", "content": answer}
        )