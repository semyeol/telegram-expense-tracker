from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from .ai_parser import categorize_transaction

load_dotenv()

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

    AUTHORIZED_USER = int(os.getenv('TELEGRAM_USER_ID', 0))

    if user_id != AUTHORIZED_USER:
        print("User is unauthorized")
        return {"ok": True}
    
    # if successful parsing and data added to google sheets:
      # send good reply
    # else, send an error message

    print(f"Received message from user {user_id}: {text}, chat_id: {chat_id}, (timestamp: {timestamp})")

    result = categorize_transaction(text)
    print(result)

    return {"ok": True}


