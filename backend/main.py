# backend/main.py
import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx
from backend.tools import calculate, calculate_schema  # <--- NEW: Import our tool

load_dotenv()

app = FastAPI()

# 1. CORS Setup (Who can talk to us?)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "https://datatype.org",
        "https://www.datatype.org"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# 2. The Tool Map (Links the name 'calculate' to the actual Python function)
available_tools = {
    "calculate": calculate
}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API Key missing")

    messages = [
    {"role": "system", "content": "Use the calculator tool if needed for math. You are AI assistant named Aryaman. You are extemely polite and replies to message by saying - Aryaman thinks/feels/suggests/.. whereever necessary "},
    {"role": "user", "content": request.message}
    ]

    # 3. First Call: Ask the AI (providing the tools)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://datatype.org",
                },
                json={
                    "model": "openai/gpt-4o-mini", # Smart model that supports tools
                    "messages": messages,
                    "tools": [calculate_schema],
                    "tool_choice": "auto"
                },
                timeout=60.0 
            )
            response.raise_for_status()
            ai_msg = response.json()["choices"][0]["message"]
            
            # 4. Check: Did the AI ask to use a tool?
            if ai_msg.get("tool_calls"):
                tool_call = ai_msg["tool_calls"][0]
                function_name = tool_call["function"]["name"]
                arguments = json.loads(tool_call["function"]["arguments"])
                
                # Run the Python function!
                if function_name in available_tools:
                    function_to_call = available_tools[function_name]
                    result = function_to_call(**arguments)
                    
                    # 5. Add the result to memory and ask AI again
                    messages.append(ai_msg) # The AI's request
                    messages.append({       # The Result
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": str(result)
                    })
                    
                    # Final Call: Get the answer based on the calculation
                    final_response = await client.post(
                        API_URL,
                        headers={"Authorization": f"Bearer {API_KEY}"},
                        json={
                            "model": "openai/gpt-4o-mini",
                            "messages": messages
                        },
                        timeout=60.0
                    )
                    return {"reply": final_response.json()["choices"][0]["message"]["content"]}
            
            # If no tool was needed, just return the text
            return {"reply": ai_msg["content"]}

        except Exception as e:
            print(f"Error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))