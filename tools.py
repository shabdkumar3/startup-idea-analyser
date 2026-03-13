from langchain_community.tools import DuckDuckGoSearchRun, TavilySearchResults
from dotenv import load_dotenv
import os

load_dotenv()

s_ddg = DuckDuckGoSearchRun()

_s_tavily = None

def _get_tavily():
    global _s_tavily
    if _s_tavily is None:
        key = os.getenv("TAVILY_API_KEY", "").strip().strip('"')
        if not key:
            return None
        try:
            _s_tavily = TavilySearchResults(max_results=3, tavily_api_key=key)
        except Exception:
            return None
    return _s_tavily


def search_web(query: str) -> str:
    results = []

    
    try:
        r = s_ddg.invoke(query)
        results.append(f"[DDG]:\n{r[:1500]}")
    except Exception as e:
        results.append(f"[DDG]: failed — {e}")

   
    tavily = _get_tavily()
    if tavily:
        try:
            r = tavily.invoke(query)
            if isinstance(r, list):
                combined = "\n".join([item.get("content", "") for item in r])
            else:
                combined = str(r)
            results.append(f"[Tavily]:\n{combined[:1500]}")
        except Exception as e:
            results.append(f"[Tavily]: failed — {e}")
    else:
        results.append("[Tavily]: skipped — TAVILY_API_KEY not set")

    return "\n\n".join(results)[:4000]