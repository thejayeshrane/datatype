import os
import json
import io
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx

# --- IMPORTS FOR AGENTS ---
from backend.tools import calculate, calculate_schema  # Agent 002 (Math)
from backend.pdf_engine import ingest_pdf, search_pdf  # Agent 003 (PDF)

load_dotenv()

app = FastAPI()

# 1. CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for now (easier for mobile/testing)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# --- AGENT 002: MATH BOT ---
available_tools = { "calculate": calculate }

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not API_KEY: raise HTTPException(status_code=500, detail="API Key missing")

    messages = [
        {"role": "system", "content": "You are Aryaman. Use the calculator tool if needed. Be polite."},
        {"role": "user", "content": request.message}
    ]

    async with httpx.AsyncClient() as client:
        try:
            # 1. Ask AI
            response = await client.post(
                API_URL,
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={
                    "model": "openai/gpt-4o-mini",
                    "messages": messages,
                    "tools": [calculate_schema],
                    "tool_choice": "auto"
                },
                timeout=60.0
            )
            response.raise_for_status()
            ai_msg = response.json()["choices"][0]["message"]

            # 2. Check for Tool Use
            if ai_msg.get("tool_calls"):
                tool_call = ai_msg["tool_calls"][0]
                func_name = tool_call["function"]["name"]
                args = json.loads(tool_call["function"]["arguments"])
                
                if func_name in available_tools:
                    result = available_tools[func_name](**args)
                    
                    # 3. Feed result back to AI
                    messages.append(ai_msg)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": str(result)
                    })
                    
                    final_res = await client.post(
                        API_URL,
                        headers={"Authorization": f"Bearer {API_KEY}"},
                        json={"model": "openai/gpt-4o-mini", "messages": messages},
                        timeout=60.0
                    )
                    return {"reply": final_res.json()["choices"][0]["message"]["content"]}
            
            return {"reply": ai_msg["content"]}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# --- AGENT 003: PDF ANALYST ---
@app.post("/agent/pdf")
async def chat_with_pdf(
    file: UploadFile = File(None),
    question: str = Form(...)
):
    # A. Handle File Upload
    if file:
        content = await file.read()
        file_stream = io.BytesIO(content)
        num_chunks = ingest_pdf(file_stream, file.filename)
        return {"response": f"Analyzing {file.filename}... split into {num_chunks} memory fragments."}

    # B. Handle Question
    if question:
        context = search_pdf(question)
        
        system_prompt = f"You are a PDF Analyst. Answer using ONLY this context: {context}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                API_URL,
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={
                    "model": "openai/gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question}
                    ]
                },
                timeout=60.0
            )
            return {"response": response.json()["choices"][0]["message"]["content"]}