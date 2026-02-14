import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://datatype.org",
        "X-Title": "Datatype Agent",
    }
    
    payload = {
        # 'openrouter/free' is the most stable free-only router
        "model": "openrouter/free", 
        "messages": [
            {"role": "system", "content": "Your name is Echo Bot. You are general AI assistant"},
            {"role": "user", "content": request.message}
        ]
    }

    async with httpx.AsyncClient() as client:
        try:
            # We add a 20-second timeout to handle busy free queues
            response = await client.post(url, json=payload, headers=headers, timeout=20.0)
            
            if response.status_code == 429:
                return {"reply": "[SYSTEM]: All free lanes are currently congested. Retrying in 30s..."}

            if response.status_code != 200:
                print(f"❌ Detail: {response.text}")
                return {"reply": f"[SYSTEM ERROR]: Uplink Code {response.status_code}"}

            data = response.json()
            # This tells you which specific free model finally picked up your call
            actual_model = data.get("model", "unknown-free-model")
            bot_reply = data["choices"][0]["message"]["content"]
            
            print(f"✅ Connection successful via: {actual_model}")
            return {"reply": bot_reply}
            
        except Exception as e:
            return {"reply": f"[CONNECTION ERROR]: {str(e)}"}

@app.get("/")
def read_root():
    return {"status": "Online", "mode": "Free Router Active"}