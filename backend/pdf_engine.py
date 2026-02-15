# --- MAGIC FIX FOR RENDER SQLITE ERROR ---
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# -----------------------------------------

import PyPDF2
import chromadb
from chromadb.utils import embedding_functions


# 1. Setup the Database (Lives in your RAM for speed)
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="pdf_data")

# 2. Function to Process the Uploaded PDF
def ingest_pdf(file_bytes, filename):
    # A. Read the PDF
    pdf_reader = PyPDF2.PdfReader(file_bytes)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    # B. Chunk the text (Split into smaller pieces so AI can read it)
    # We split by roughly 1000 characters
    chunk_size = 1000
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    # C. Store in Vector DB
    # We generate IDs like "doc_0", "doc_1"
    ids = [f"{filename}_{i}" for i in range(len(chunks))]
    metadatas = [{"source": filename} for _ in chunks]
    
    # This automatically converts text -> numbers (embeddings)
    collection.add(
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )
    return len(chunks)

# 3. Function to Search the PDF
def search_pdf(query):
    results = collection.query(
        query_texts=[query],
        n_results=3 # Get top 3 most relevant chunks
    )
    # Combine the found text into one string
    context = " ".join(results['documents'][0])
    return context