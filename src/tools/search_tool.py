import time
from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from src.memory import global_ledger

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None


class SearchInput(BaseModel):
    query: str = Field(description="Targeted search query to execute on the web")
    max_results: int = Field(default=3, description="Maximum number of search results to return")


class WebSearchTool(BaseTool):
    name: str = "Live Web Search"
    description: str = (
        "Performs a live web search using DuckDuckGo. Returns indexed results containing "
        "titles, canonical URLs, and extracted factual snippets. Use this to discover facts, "
        "verify company details, and locate citations."
    )
    args_schema: Type[BaseModel] = SearchInput

    def _run(self, query: str, max_results: int = 3) -> str:
        """Executes DuckDuckGo search and formats citations."""
        if not DDGS:
            return "Error: DuckDuckGo search library is not installed."

        try:
            ddgs_client = DDGS()
            raw_results = list(ddgs_client.text(query, max_results=max_results))
            if not raw_results:
                # Agentic feedback: tell agent nothing was found so it adapts query
                return (
                    f"OBSERVATION: No results found for query '{query}'. "
                    f"STRATEGY RECOMMENDATION: The query might be too narrow or misspelled. "
                    f"Please adapt your query with alternative keywords or broader terms."
                )

            formatted_results = []
            for idx, r in enumerate(raw_results, start=1):
                title = r.get("title", "No Title")
                url = r.get("href", r.get("url", "No URL"))
                body = r.get("body", r.get("snippet", ""))

                formatted_results.append(
                    f"[Result {idx}]\n"
                    f"Title: {title}\n"
                    f"URL: {url}\n"
                    f"Snippet: {body}\n"
                )

            output_text = (
                f"OBSERVATION: Returned {len(raw_results)} results for query: '{query}'\n\n"
                + "\n".join(formatted_results)
            )

            # Record tool call in audit ledger
            global_ledger.record_cycle(
                iteration=global_ledger.iteration_count,
                agent="Autonomous Research Agent",
                phase="ACT",
                observation=f"Executed search query '{query}'",
                decision="Inspect returned snippets and evaluate if sufficient or if follow-up query is needed",
                tool_called="Live Web Search",
                tool_input={"query": query, "max_results": max_results},
                tool_output_summary=f"Surfaced {len(raw_results)} results",
                evaluation="Pending analysis of evidence content",
                next_action="Register facts with Evidence Evaluator or formulate refined search query",
            )

            return output_text

        except Exception as e:
            error_msg = f"Search encountered an exception: {str(e)}. Try refining your query."
            global_ledger.record_cycle(
                iteration=global_ledger.iteration_count,
                agent="Autonomous Research Agent",
                phase="ACT",
                observation=f"Search failed for '{query}' with error: {str(e)}",
                decision="Pivot search query or retry",
                tool_called="Live Web Search",
                tool_input={"query": query},
                tool_output_summary="Failed with exception",
                evaluation="Network/Rate limit issue",
                next_action="Adapt query or proceed with cached knowledge",
            )
            return error_msg
