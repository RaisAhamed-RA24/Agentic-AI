
import os
import time
from urllib.parse import urlparse

from dotenv import load_dotenv
from tavily import TavilyClient
from google import genai


# ==========================================
# 1. LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

tavily_api_key = os.getenv("TAVILY_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not tavily_api_key or not gemini_api_key:
    raise ValueError("API keys missing. Check your .env file.")


# ==========================================
# 2. INITIALIZE API CLIENTS
# ==========================================

tavily = TavilyClient(api_key=tavily_api_key)
client = genai.Client(api_key=gemini_api_key)


# ==========================================
# 3. SOURCE CLASSIFICATION FUNCTION
# ==========================================

def classify_source(url):

    domain = urlparse(url).hostname

    if not domain:
        return "Unknown Source"

    domain = domain.lower()

    # Academic and research sources
    if (
        domain == "arxiv.org"
        or domain.endswith(".arxiv.org")
        or domain.endswith(".ncbi.nlm.nih.gov")
    ):
        return "Academic / Research"

    # Professional organizations
    elif domain == "ama-assn.org" or domain.endswith(".ama-assn.org"):
        return "Professional Organization"

    # Medical institutions
    elif domain == "mayoclinic.org" or domain.endswith(".mayoclinic.org"):
        return "Medical Institution"

    # General reference sources
    elif domain == "wikipedia.org" or domain.endswith(".wikipedia.org"):
        return "General Reference"

    # Official publishers
    elif domain == "marvel.com" or domain.endswith(".marvel.com"):
        return "Official Publisher"

    # Commercial platforms
    elif domain == "netflix.com" or domain.endswith(".netflix.com"):
        return "Commercial Platform"

    # Developer platforms
    elif domain == "github.com" or domain.endswith(".github.com"):
        return "Developer Platform"

    # Government sources
    elif domain.endswith(".gov") or domain.endswith(".gov.in"):
        return "Government Source"

    # Educational institutions
    elif domain.endswith(".edu") or domain.endswith(".ac.in"):
        return "Educational Institution"

    else:
        return "Unclassified"


# ==========================================
# 4. SOURCE CREDIBILITY EVALUATION
# ==========================================

def evaluate_credibility(source_type):

    credibility_scores = {
        "Academic / Research": 0.95,
        "Government Source": 0.95,
        "Medical Institution": 0.90,
        "Professional Organization": 0.85,
        "Educational Institution": 0.80,
        "Official Publisher": 0.75,
        "Developer Platform": 0.70,
        "Commercial Platform": 0.60,
        "General Reference": 0.55,
        "Unclassified": 0.40,
        "Unknown Source": 0.30
    }

    return credibility_scores.get(source_type, 0.30)


# ==========================================
# 5. GET RESEARCH TOPIC
# ==========================================

topic = input("\nEnter your research topic: ").strip()

if not topic:
    raise ValueError("Research topic cannot be empty.")

print("\nSearching the web for:", topic)


# ==========================================
# 6. SEARCH USING TAVILY
# ==========================================

response = tavily.search(
    query=topic,
    max_results=5
)

results = response.get("results", [])

print("\n========== TAVILY SEARCH RESULTS ==========\n")

for result in results:

    source_type = classify_source(result["url"])
    credibility_score = evaluate_credibility(source_type)

    print("Title:", result["title"])
    print("URL:", result["url"])
    print("Source Type:", source_type)
    print("Relevance Score:", result["score"])
    print("Credibility Score:", credibility_score)
    print("Content:", result["content"])
    print("-" * 50)


# ==========================================
# 7. FILTER RESULTS BY RELEVANCE
# ==========================================

filtered_results = [
    result for result in results
    if result["score"] >= 0.65
]

print("\nTotal search results:", len(results))
print("Relevant search results:", len(filtered_results))


# ==========================================
# 8. HANDLE EMPTY SEARCH RESULTS
# ==========================================

if not filtered_results:

    print("\nNo sufficiently relevant search results found.")
    print("Try a more specific research topic.")

    raise SystemExit


# ==========================================
# 9. PREPARE SEARCH CONTEXT
# ==========================================

search_context = ""

for index, result in enumerate(filtered_results, start=1):

    source_type = classify_source(result["url"])
    credibility_score = evaluate_credibility(source_type)

    published_date = result.get(
        "published_date",
        "Not available"
    )

    search_context += f"""
Source {index}
Title: {result["title"]}
URL: {result["url"]}
Source Type: {source_type}
Credibility Score: {credibility_score}
Published Date: {published_date}
Content: {result["content"]}
Relevance Score: {result["score"]}
-----------------------------------
"""

print("\n========== PREPARED SEARCH CONTEXT ==========\n")
print(search_context)


# ==========================================
# 10. CREATE GEMINI PROMPT
# ==========================================

prompt = f"""
You are an AI research assistant.

Research Topic: {topic}

Analyze the following web search results:

{search_context}

Prepare a structured research report containing:

1. Introduction
2. Key Findings
3. Important Concepts
4. Benefits and Applications
5. Challenges
6. Conclusion
7. Sources

Important instructions:

- Base your report on the provided search results.
- Do not invent facts or sources.
- Include source URLs when presenting findings.
- Distinguish academic research, professional organizations,
  medical institutions, government sources, and general references.
- Do not assume a source is trustworthy solely because of its category
  or assigned credibility score.
- If sources disagree, explain the disagreement.
- If publication dates are unavailable, do not invent them.
- If information is insufficient, mention it clearly.
- Do not present unsupported claims as established facts.
"""


# ==========================================
# 11. GENERATE REPORT WITH RETRY MECHANISM
# ==========================================

print("\nSending research context to Gemini...")

max_retries = 3

for attempt in range(1, max_retries + 1):

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        print("\n========== AI RESEARCH REPORT ==========\n")
        print(response.text)
        print("\n========================================")

        break

    except Exception as e:

        error_message = str(e)

        retryable = (
            "503" in error_message
            or "UNAVAILABLE" in error_message
            or "429" in error_message
            or "RESOURCE_EXHAUSTED" in error_message
        )

        if retryable and attempt < max_retries:

            wait_seconds = 2 ** attempt

            print(
                f"\nGemini temporarily unavailable."
                f"\nAttempt {attempt} of {max_retries} failed."
            )

            print(f"Retrying in {wait_seconds} seconds...")

            time.sleep(wait_seconds)

        else:

            print("\nUnable to generate the research report.")
            print("Error:", error_message)

            if retryable:
                print("Maximum retry attempts reached.")

            break
