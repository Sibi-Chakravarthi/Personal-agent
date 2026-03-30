import os
from tavily import TavilyClient

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query: str) -> str:
    response = client.search(query=query, max_results=3)
    results = response.get("results", [])
    if not results:
        return "No results found."
    return "\n\n".join(
        f"**{r['title']}**\n{r['content'][:300]}"
        for r in results
    )