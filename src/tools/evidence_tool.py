from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from src.memory import global_ledger


class RegisterEvidenceInput(BaseModel):
    fact: str = Field(description="A concise, verified factual finding")
    source_title: str = Field(description="Title of the web source where this was found")
    source_url: str = Field(description="URL of the web source")
    snippet: str = Field(description="Exact snippet or quote from the search result")
    query_used: str = Field(description="The query that found this evidence")
    confidence: float = Field(default=0.85, description="Confidence in this fact (0.0 to 1.0)")
    information_gaps_remaining: str = Field(
        default="",
        description="Specific facts or topics still missing to complete the research objective"
    )
    is_research_complete: bool = Field(
        default=False,
        description="Set to true if verified evidence is now sufficient to stop searching"
    )


class EvidenceEvaluatorTool(BaseTool):
    name: str = "Evidence Evaluator & Ledger"
    description: str = (
        "Registers a verified factual finding with its source citation into the shared Evidence Ledger. "
        "Allows the Research Agent to log findings, update confidence, identify missing knowledge gaps, "
        "and signal whether research sufficiency has been reached to conclude the search phase."
    )
    args_schema: Type[BaseModel] = RegisterEvidenceInput

    def _run(
        self,
        fact: str,
        source_title: str,
        source_url: str,
        snippet: str,
        query_used: str,
        confidence: float = 0.85,
        information_gaps_remaining: str = "",
        is_research_complete: bool = False,
    ) -> str:
        # Register evidence in memory
        item = global_ledger.add_evidence(
            fact=fact,
            source_title=source_title,
            source_url=source_url,
            snippet=snippet,
            query_used=query_used,
            confidence=confidence,
        )

        if information_gaps_remaining.strip():
            global_ledger.remaining_gaps = [
                g.strip() for g in information_gaps_remaining.split(";") if g.strip()
            ]
        else:
            global_ledger.remaining_gaps = []

        status_text = "COMPLETE (Sufficient evidence found)" if is_research_complete else "IN PROGRESS (Gaps remain)"

        # Record audit cycle
        global_ledger.record_cycle(
            iteration=global_ledger.iteration_count,
            agent="Autonomous Research Agent",
            phase="EVALUATE",
            observation=f"Registered evidence {item.id}: '{fact[:60]}...'",
            decision=f"Status: {status_text}. Missing: {information_gaps_remaining or 'None'}",
            tool_called="Evidence Evaluator & Ledger",
            tool_input={
                "fact": fact,
                "url": source_url,
                "confidence": confidence,
                "is_complete": is_research_complete,
            },
            tool_output_summary=f"Stored {item.id}. Total evidence count: {len(global_ledger.evidence)}",
            evaluation=f"Confidence: {confidence:.2f}, Sufficient: {is_research_complete}",
            next_action="Halt research and proceed to outreach" if is_research_complete else "Formulate targeted query to bridge remaining gaps",
        )

        return (
            f"SUCCESS: Recorded {item.id} in Evidence Ledger.\n"
            f"- Total verified evidence items: {len(global_ledger.evidence)}\n"
            f"- Research Status: {status_text}\n"
            f"- Remaining Gaps: {information_gaps_remaining or 'None'}\n"
            f"If complete, conclude your research summary. If not complete, choose your next query targeting the gaps."
        )
