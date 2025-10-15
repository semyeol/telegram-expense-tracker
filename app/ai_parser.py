import os

from dotenv import load_dotenv
from google import genai
from utils import categorize_transaction, build_prompt

load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=gemini_key)
model = "gemini-2.0-flash-lite"
config = {"temperature": 0.1, "max_output_tokens": 500}
prompt = build_prompt(raw_text)
contents = {"role": 'user', "text": prompt}

response = client.models.generate_content(
    model, config, contents
)

print(response.text)



def main():
    pass


if __name__ == "__main__":
    main()
