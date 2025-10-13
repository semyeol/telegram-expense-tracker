from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

gemini_key = os.getenv('GEMINI_API_KEY')

client = genai.Client(api_key=gemini_key)

response = client.models.generate_content(
    model="gemini-2.0-flash-lite", contents="how are you doing today"
)

print(response.text)