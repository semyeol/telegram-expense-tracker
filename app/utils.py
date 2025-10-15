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


INCOME_CATEGORIES = ["Work", "Other"]
SAVINGS_CATEGORIES = ["Wealthfront"]
INVESTING_CATEGORIES = ["Individual", "Roth IRA", "401k", "ESPP"]
BILLS_CATEGORIES = ["Parents", "Wifi", "Gym", "Subscriptions"]
EXPENSE_CATEGORIES = [
    "Eating Out",
    "Shopping",
    "Activity",
    "Grocery",
    "Transporation",
    "School",
    "Other",
]


# for gemini
def categorize_transaction(raw_text: str):
    pass


# for gemini
def build_prompt(raw_text: str):
    return f"""
You are a financial transaction categorizer.
Analyze this transaction text: {raw_text}

Determine both the transaction type and category from these options:
Income: {", ".join(INCOME_CATEGORIES)}
Savings: {", ".join(SAVINGS_CATEGORIES)}
Investing: {", ".join(INVESTING_CATEGORIES)}
Bills: {", ".join(BILLS_CATEGORIES)}
Expenses: {", ".join(EXPENSE_CATEGORIES)}

Extract the amount and create a description with the following valid JSON format only:

    {
        "type": "income|"savings"|"investing"|"bills"|"expense",
      "description": "clean, concise description",
      "amount": number,
      "category": "exact category from the list above",
      "confidence": number between 0 and 1
    }

    Examples: 
    - "mcdonalds, 12" → {
        "type": "expense", "description": "McDonald's", "amount": 12, "category": "Eating Out", "confidence": 0.95}
    - "wealthfront, 500" → {
        "type": "savings", "description": "Savings deposit", "amount": 500, "category": "Wealthfront", "confidence": 0.90}
    - "gym membership 25" → {
        "type": "bills", "description": "Gym membership", "amount": 25, "category": "Gym", "confidence": 0.96}
    - "golf 33" → {
        "type": "expense", "description": "Golf", "amount": 33, "category": "Activity", "confidence": 0.97}
"""
