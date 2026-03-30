from tools.search import search_web

TOOLS = {
    "search_web": {
        "description": "Search the internet for current information. Input: {'query': 'your search query'}",
        "fn": search_web
    }
}

def execute_tool(name: str, input_data: dict) -> str:
    if name not in TOOLS:
        return f"Error: Tool '{name}' not found."
    try:
        return TOOLS[name]["fn"](**input_data)
    except Exception as e:
        return f"Tool error: {str(e)}"