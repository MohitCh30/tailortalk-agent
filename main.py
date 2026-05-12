from fastapi import FastAPI
from pydantic import BaseModel
from agent import chat
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: MessageRequest):
    response = chat(request.message)
    return {"response": response}

@app.get("/health")
async def health():
    return {"status": "ok"}