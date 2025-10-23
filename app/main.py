from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv
from .ai_parser import categorize_transaction
from .sheets import get_spreadsheet, append_transaction
from .utils import send_reply

load_dotenv()
app = FastAPI()

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
        print(f"Unauthorized user: {user_id} attempted to send message.")
        await send_reply(chat_id, "User is unauthorized!")
        return {"ok": True}

    # print(f"received message from user {user_id}: {text}, chat_id: {chat_id}, (timestamp: {timestamp})")

    # 1. categorize
    result = categorize_transaction(text)

    if not result:
        print(f"AI parsing failed for message: {text}")
        await send_reply(chat_id, "AI failed to parse message xD")
        return {"ok": True}

    # 2: get or create spreadsheet for the year
    try:
        spreadsheet_id = get_spreadsheet(timestamp)
        print(f"Spreadsheet retrieved: {spreadsheet_id}")
    except Exception as e:
        print("Error getting spreadsheet")
        await send_reply(chat_id, "Error getting spreadsheet...")
        return {"ok": True}

    # 3: append transaction to sheet
    success = append_transaction(spreadsheet_id, timestamp, result)

    if success:
        description = result['description']
        amount = result['amount']
        print(f"Successfully added: {result['description']} - ${result['amount']}")
        await send_reply(chat_id, f"Added {description} : ${amount}!")
    else:
        # low confidence or append failed
        confidence = result.get("confidence", 0)
        if confidence <= 0.90:
            print(f"Low confidence ({confidence}), transaction not added")
            await send_reply(chat_id, f"The model was not confident in it's answer. \nConfidence: {confidence}")
        else:
            print("Failed to add transaction to sheet")
            await send_reply(chat_id, "Failed to add transaction.")

    return {"ok": True}


