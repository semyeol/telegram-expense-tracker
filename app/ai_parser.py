import os
from dotenv import load_dotenv
from google import genai
import json
import re

load_dotenv()

INCOME_CATEGORIES = ["Work", "Other"]
SAVINGS_CATEGORIES = ["Wealthfront"]
INVESTING_CATEGORIES = ["Individual", "Roth IRA", "401k", "ESPP"]
BILLS_CATEGORIES = ["Parents", "Wifi", "Gym", "Subscriptions"]
EXPENSE_CATEGORIES = [
    "Eating Out",
    "Shopping",
    "Activity",
    "Grocery",
    "Transportation",
    "School",
    "Other",
]


def build_prompt(raw_text: str):
    return f"""You are a financial transaction categorizer.
Analyze this transaction text: {raw_text}

Determine both the transaction type and category from these options:
- Income: {", ".join(INCOME_CATEGORIES)}
- Savings: {", ".join(SAVINGS_CATEGORIES)}
- Investing: {", ".join(INVESTING_CATEGORIES)}
- Bills: {", ".join(BILLS_CATEGORIES)}
- Expenses: {", ".join(EXPENSE_CATEGORIES)}

Extract the amount and create a description. Return ONLY valid JSON in this exact format:

{{
    "type": "income|savings|investing|bills|expense",
    "description": "clean, concise description",
    "amount": number,
    "category": "exact category from the list above",
    "confidence": number between 0 and 1
}}

Examples:
- "mcdonalds, 12" → {{"type": "expense", "description": "McDonald's", "amount": 12, "category": "Eating Out", "confidence": 0.95}}
- "wealthfront, 500" → {{"type": "savings", "description": "Savings deposit", "amount": 500, "category": "Wealthfront", "confidence": 0.90}}
- "gym membership 25" → {{"type": "bills", "description": "Gym membership", "amount": 25, "category": "Gym", "confidence": 0.96}}
- "golf 33" → {{"type": "expense", "description": "Golf", "amount": 33, "category": "Activity", "confidence": 0.97}}

Return only the JSON object, no additional text."""


def categorize_transaction(raw_text: str):
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        model_id = "gemini-2.0-flash-lite"
        
        prompt = build_prompt(raw_text)
        
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config={"temperature": 0.1, "max_output_tokens": 500}
        )
        
        # parse response
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(response.text)
        
    except Exception as e:
        print(f"Error categorizing transaction: {e}")
        return None


if __name__ == "__main__":
    test = "starbucks 5.50"
    result = categorize_transaction(test)
    print(json.dumps(result, indent=2))
