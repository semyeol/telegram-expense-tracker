import os
from dotenv import load_dotenv
from google import genai
from openai import OpenAI
import json
import re
import time

load_dotenv()

INCOME_CATEGORIES = ["Work", "Other"]
SAVINGS_CATEGORIES = ["Wealthfront"]
INVESTING_CATEGORIES = ["Individual", "Roth IRA", "ESPP"]
EXPENSES_CATEGORIES = [
    "Parents",
    "Wifi",
    "Subscriptions",
    "Eating Out",
    "Shopping",
    "Activity",
    "Grocery",
    "Personal Care",
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
- Expenses: {", ".join(EXPENSES_CATEGORIES)}

Extract the amount and create a description. Return ONLY valid JSON in this exact format:

{{
    "type": "income|savings|investing|expenses",
    "description": "clean, concise description",
    "amount": number,
    "category": "exact category from the list above",
    "confidence": number between 0 and 1
}}

Examples:
- "mcdonalds, 12" → {{"type": "expenses", "description": "McDonald's", "amount": 12, "category": "Eating Out", "confidence": 0.95}}
- "wealthfront, 500" → {{"type": "savings", "description": "Savings deposit", "amount": 500, "category": "Wealthfront", "confidence": 0.90}}
- "gym membership 25" → {{"type": "expenses", "description": "Gym membership", "amount": 25, "category": "Gym", "confidence": 0.96}}
- "golf 33" → {{"type": "expenses", "description": "Golf", "amount": 33, "category": "Activity", "confidence": 0.97}}

Return only the JSON object, no additional text."""


def categorize_with_gemini(raw_text: str):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"), http_options={'timeout': 100})
    model_id = "gemini-2.0-flash"

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


def categorize_with_openai(raw_text: str):
    """Fallback to OpenAI API"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = build_prompt(raw_text)

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "user", "content": prompt}
        ],
        # lower temp = more deterministic, follows directions
        # higher temp = more creative
        temperature=0.1,
        max_completion_tokens=500
    )

    # different parsing than gemini
    content = response.choices[0].message.content

    if not content:
        print("OpenAI returned empty response.")
        raise ValueError("OpenAI returned empty response")

    # print(f"OpenAI response: {content}")

    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    return json.loads(content)


def categorize_transaction(raw_text: str):
    # try Gemini first
    for attempt in range(3):
        try:
            result = categorize_with_gemini(raw_text)
            print(f"Categorized with Gemini (attempt {attempt + 1})")
            return result
        except Exception as e:
            print(f"Gemini error (attempt {attempt + 1}): {e}")
            if attempt < 2:
                time.sleep(2)

    # Openai fallback
    print("Falling back to OpenAI...")
    try:
        result = categorize_with_openai(raw_text)
        print("Categorized with OpenAI")
        return result
    except Exception as e:
        print(f"OpenAI error: {e}")
        return None


if __name__ == "__main__":
    test = "golf, 45"
    result = categorize_transaction(test)
    print(json.dumps(result, indent=2))
