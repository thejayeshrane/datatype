# --- MAGIC FIX FOR RENDER SQLITE ERROR ---
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# -----------------------------------------

import io
import os
import PyPDF2
import chromadb
from openai import OpenAI

# 1. Setup Database
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="pdf_data")

# 2. Setup OpenRouter Client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def ingest_pdf(file_bytes, filename):
    try:
        pdf_stream = io.BytesIO(file_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_stream)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        
        chunk_size = 1000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        if not chunks: return 0

        ids = [f"{filename}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename} for _ in chunks]
        collection.add(documents=chunks, metadatas=metadatas, ids=ids)
        return len(chunks)
    except Exception as e:
        print(f"Ingest Error: {e}")
        return 0

def search_pdf(query):
    # A. Search Database
    results = collection.query(query_texts=[query], n_results=3)
    
    if not results['documents'] or not results['documents'][0]:
        return "I couldn't find relevant info in the uploaded document."
        
    context = " ".join(results['documents'][0])
    
    # B. Generate Answer via OpenRouter
    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Answer using ONLY the context provided."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Error: {str(e)}"