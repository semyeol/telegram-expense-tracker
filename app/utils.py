import httpx
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
REPLY_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


# telegram bot's response
async def send_reply(chat_id: int, text: str):
    async with httpx.AsyncClient() as client:
        await client.post(REPLY_URL, json={"chat_id": chat_id, "text": text})
