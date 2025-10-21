from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from .ai_parser import categorize_transaction
from .sheets import get_spreadsheet, append_transaction

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

    print(f"Received message from user {user_id}: {text}, chat_id: {chat_id}, (timestamp: {timestamp})")

    # 1. categorize
    result = categorize_transaction(text)

    if not result:
        print("AI parsing failed")
        # TODO: Send Telegram message: "Could not parse transaction"
        return {"ok": True}

    print(f"AI parsed result: {result}")

    # 2: get or create spreadsheet for the year
    try:
        spreadsheet_id = get_spreadsheet(timestamp)
        print(f"Using spreadsheet: {spreadsheet_id}")
    except Exception as e:
        print(f"Error getting spreadsheet: {e}")
        # TODO: Send Telegram message: "Error accessing spreadsheet"
        return {"ok": True}

    # 3: append transaction to sheet
    success = append_transaction(spreadsheet_id, timestamp, result)

    if success:
        print(f"Successfully added: {result['description']} - ${result['amount']}")
        # TODO: Send Telegram message: "Added: {description} - ${amount}"
    else:
        # ow confidence or append failed
        confidence = result.get("confidence", 0)
        if confidence <= 0.90:
            print(f"Low confidence ({confidence}), transaction not added")
            # TODO: Send Telegram message: "AI was not confident in parsing. Please try again."
        else:
            print("Failed to append transaction to sheet")
            # TODO: Send Telegram message: "Failed to save transaction"

    return {"ok": True}


