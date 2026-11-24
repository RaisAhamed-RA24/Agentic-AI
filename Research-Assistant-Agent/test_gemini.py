import os
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Gemini API key not found!")

client = genai.Client(api_key=api_key)

print("Connecting to Gemini...")

try:
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents="Explain what an AI agent is in simple language with one real-world example."
    )

    print("\n========== GEMINI RESPONSE ==========\n")
    print(response.text)

except errors.APIError as e:
    print("\nGemini API Error!")
    print("Status code:", e.code)
    print("Message:", e.message)

    if e.code == 503:
        print("The model is temporarily unavailable. Try again later.")

    elif e.code == 429:
        print("API usage limit reached. Check your quota.")

    elif e.code == 404:
        print("Model not found. Check available model IDs.")

except Exception as e:
    print("\nUnexpected error:", e)
