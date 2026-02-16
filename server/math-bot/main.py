from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Important for security

app = FastAPI()

# SECURITY: This allows your website (frontend) to talk to your server (backend).
# Without this, the browser will block the connection.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "https://datatype.org", 
    "http://127.0.0.1:5500", 
    "http://localhost:8000"], # This needs to work  on localhost for testing and on domain as well.
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "Online", "agent": "Math-Engine-001"}

@app.get("/calculate")
def calculate(expression: str):
    try:
        # 'eval' is a simple way to solve math strings in Python.
        # Professional tip: In real AI apps, we use 'math' libraries for safety.
        result = eval(expression)
        return {
            "input": expression,
            "answer": result,
            "status": "success"
        }
    except Exception as e:
        # If the user types "hello" instead of math, we return an error.
        raise HTTPException(status_code=400, detail="Invalid mathematical expression")
    
if __name__ == "__main__":
    import uvicorn
    import os
    # Render provides the 'PORT' environment variable automatically
    port = int(os.environ.get("PORT", 8000)) 
    uvicorn.run(app, host="0.0.0.0", port=port)