from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
# Import the engine we just fixed
from backend.pdf_engine import ingest_pdf, search_pdf 

app = FastAPI()

# --- SECURITY GATE (CORS) ---
# This tells the server: "Accept requests from ANYWHERE (localhost or web)"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ----------------------------

@app.get("/")
def home():
    return {"status": "Agent 003 Online", "system": "Operational"}

@app.post("/agent/pdf")
async def agent_pdf(file: UploadFile = File(None), question: str = Form(None)):
    try:
        # SCENARIO 1: User Uploads a File
        if file:
            content = await file.read()
            # Send to our PDF Engine
            chunks = ingest_pdf(content, file.filename) 
            return {"response": f"**UPLOAD COMPLETE:** Processed {file.filename} into {chunks} memory fragments. Ready for analysis."}
        
        # SCENARIO 2: User Asks a Question
        if question:
            # Search our PDF Engine
            result = search_pdf(question)
            return {"response": result}
            
        return {"response": "System Idle. Please upload a document."}

    except Exception as e:
        return {"response": f"**SYSTEM ERROR:** {str(e)}"}