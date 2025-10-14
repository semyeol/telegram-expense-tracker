from fastapi import FastAPI, Request
import json
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

class Message(BaseModel):
    text: str

"""
message format
{
  "message": {
    "chat": { "id": 12345 },
    "from": { "id": 12345 },
    "text": "McDonald's, 12",
    "date": 1717446600
  }
}
"""

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text")
    user_id = message.get("from", {}).get("id")
    timestamp = message.get("date")

    print(f"Received message from user {user_id}: {text} (timestamp: {timestamp})")

    return {"ok": True}
