from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import uvicorn

app = FastAPI()

# Enable CORS so the Flutter app can talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str

# Local Ollama URL (Default port 11434)
OLLAMA_URL = "http://localhost:11434/api/generate"

# --- NEW ROOT ROUTE ---
# This fixes the "Not Found" error when visiting 127.0.0.1:8000 in your browser
@app.get("/")
async def root():
    return {"message": "Offline Ollama AI Server is linked and running...."}

# --- CHAT ENDPOINT ---
@app.post("/chat")
async def chat(request: ChatRequest):
    payload = {
        "model": "gemma3:1b",  # Ensure you have pulled this model in Ollama first
        "prompt": request.prompt,
        "stream": False
    }

    try:
        async with httpx.AsyncClient() as client:
            # 120 second timeout gives the local LLM enough time to "think"
            response = await client.post(OLLAMA_URL, json=payload, timeout=120.0)
            result = response.json()
            return {"response": result.get("response", "No response from AI")}

    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        # This sends a clear error back to your Flutter app if Ollama isn't running
        raise HTTPException(status_code=500, detail="Ollama server is not responding.")

if __name__ == "__main__":
    # host="0.0.0.0" allows other devices on your Wi-Fi (like your phone) to connect
    uvicorn.run(app, host="0.0.0.0", port=8000)