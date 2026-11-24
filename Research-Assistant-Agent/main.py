import time
import os
from dotenv import load_dotenv
from google import genai

# =====================================
# 1. LOAD ENVIRONMENT VARIABLES
# =====================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: Gemini API key not found in .env file.")
    exit()

# Initialize Gemini client
client = genai.Client(api_key=api_key)


# =====================================
# 2. DISPLAY APPLICATION
# =====================================

print("================================")
print("     AI RESEARCH ASSISTANT")
print("================================")


# =====================================
# 3. GET RESEARCH INPUT
# =====================================

topic = input("\nEnter your research topic: ")

print("\nSelect Research Depth:")
print("1. Beginner")
print("2. Intermediate")
print("3. Advanced")

choice = input("\nEnter your choice (1-3): ")


# =====================================
# 4. DETERMINE RESEARCH DEPTH
# =====================================

if choice == "1":
    depth = "Beginner"

elif choice == "2":
    depth = "Intermediate"

elif choice == "3":
    depth = "Advanced"

else:
    depth = "Beginner"
    print("Invalid choice. Defaulting to Beginner.")


# =====================================
# 5. GENERATE DYNAMIC PROMPT
# =====================================

if depth == "Beginner":
    instructions = """
    Explain the topic in simple language.
    Include basic concepts and real-world examples.
    """

elif depth == "Intermediate":
    instructions = """
    Explain the topic in detail.
    Include important concepts, applications,
    benefits and challenges.
    """

else:
    instructions = """
    Provide an in-depth technical explanation.
    Include advanced concepts, current developments,
    research challenges and future opportunities.
    """


prompt = f"""
You are a professional research assistant.

Research Topic: {topic}

Research Level: {depth}

Your Instructions:
{instructions}

Prepare a structured research report with:
1. Introduction
2. Key Concepts
3. Applications
4. Benefits
5. Challenges
6. Conclusion
"""


# =====================================
# 6. DISPLAY RESEARCH REQUEST
# =====================================

print("\n========== RESEARCH REQUEST ==========")
print("Topic:", topic)
print("Research Depth:", depth)
print("======================================")


# =====================================
# 7. SEND PROMPT TO GEMINI
# =====================================

print("\nResearching your topic... Please wait.")

max_attempts = 3

for attempt in range(1, max_attempts + 1):

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        print("\n========== RESEARCH REPORT ==========\n")
        print(response.text)
        print("\n====================================")

        break

    except Exception as e:

        error_message = str(e)

        if ("503" in error_message or "429" in error_message) and attempt < max_attempts:

            wait_time = 5 * attempt

            print(f"\nTemporary API issue. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

        else:
            print("\nSomething went wrong!")
            print("Error:", e)
            break