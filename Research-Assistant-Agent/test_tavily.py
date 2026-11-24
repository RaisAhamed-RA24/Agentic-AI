
import os
from dotenv import load_dotenv
from tavily import TavilyClient

# Load environment variables
load_dotenv()

# Initialize Tavily client
tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)

# Search the web
response = tavily.search(
    query="Latest developments in Artificial Intelligence",
    max_results=5
)

# Display search results
print("\n========== TAVILY SEARCH RESULTS ==========\n")

# Filter relevant search results
filtered_results = [
    result for result in response["results"]
    if result["score"] >= 0.65
]

print("\n========== FILTERED RESULTS ==========\n")

for result in filtered_results:
    print("Title:", result["title"])
    print("URL:", result["url"])
    print("Relevance Score:", result["score"])
    print("Content:", result["content"])
    print("-" * 50)

print("Total results:", len(filtered_results))