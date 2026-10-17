import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    """Represents a verified piece of evidence with exact source citation."""
    id: str = Field(description="Unique citation identifier e.g. [E1]")
    fact: str = Field(description="Key factual finding or verified claim")
    source_title: str = Field(description="Page or document title")
    source_url: str = Field(description="Canonical URL of source")
    snippet: str = Field(description="Raw supporting snippet from search")
    query_used: str = Field(description="Search query that surfaced this evidence")
    confidence: float = Field(default=0.85, description="Confidence score from 0.0 to 1.0")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class AuditRecord(BaseModel):
    """
    Tracks genuine Observe-Decide-Act-Evaluate cycles for agent accountability.
    """
    iteration: int
    agent: str
    phase: str  # OBSERVE, DECIDE, ACT, EVALUATE, LOOPBACK
    observation: str
    decision: str
    tool_called: Optional[str] = None
    tool_input: Optional[Any] = None
    tool_output_summary: Optional[str] = None
    evaluation: Optional[str] = None
    next_action: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class EvidenceLedger:
    """
    Central operational memory for the 2-Agent Crew.
    Maintains verified evidence, source citations, audit trail, and stopping criteria.
    """

    def __init__(self):
        self.evidence: List[EvidenceItem] = []
        self.audit_records: List[AuditRecord] = []
        self.research_objective: str = ""
        self.remaining_gaps: List[str] = []
        self.iteration_count: int = 0
        self.feedback_loops_count: int = 0

    def reset(self):
        self.evidence.clear()
        self.audit_records.clear()
        self.research_objective = ""
        self.remaining_gaps.clear()
        self.iteration_count = 0
        self.feedback_loops_count = 0

    def set_objective(self, objective: str):
        self.research_objective = objective

    def add_evidence(
        self,
        fact: str,
        source_title: str,
        source_url: str,
        snippet: str,
        query_used: str,
        confidence: float = 0.85
    ) -> EvidenceItem:
        eid = f"[E{len(self.evidence) + 1}]"
        item = EvidenceItem(
            id=eid,
            fact=fact,
            source_title=source_title,
            source_url=source_url,
            snippet=snippet,
            query_used=query_used,
            confidence=confidence,
        )
        self.evidence.append(item)
        return item

    def get_all_evidence(self) -> List[EvidenceItem]:
        return list(self.evidence)

    def get_formatted_citations(self) -> str:
        if not self.evidence:
            return "No verified citations recorded yet."
        lines = []
        for e in self.evidence:
            lines.append(f"{e.id} {e.fact}\n   Source: {e.source_title} ({e.source_url})")
        return "\n\n".join(lines)

    def record_cycle(
        self,
        iteration: int,
        agent: str,
        phase: str,
        observation: str,
        decision: str,
        tool_called: Optional[str] = None,
        tool_input: Optional[Any] = None,
        tool_output_summary: Optional[str] = None,
        evaluation: Optional[str] = None,
        next_action: Optional[str] = None,
    ):
        record = AuditRecord(
            iteration=iteration,
            agent=agent,
            phase=phase,
            observation=observation,
            decision=decision,
            tool_called=tool_called,
            tool_input=tool_input,
            tool_output_summary=tool_output_summary,
            evaluation=evaluation,
            next_action=next_action,
        )
        self.audit_records.append(record)

    def get_audit_trail(self) -> List[AuditRecord]:
        return list(self.audit_records)

    def export_audit_json(self, filepath: str) -> str:
        data = {
            "research_objective": self.research_objective,
            "total_iterations": self.iteration_count,
            "feedback_loops": self.feedback_loops_count,
            "evidence_count": len(self.evidence),
            "evidence_items": [e.model_dump() for e in self.evidence],
            "audit_trail": [a.model_dump() for a in self.audit_records],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return filepath


# Shared global memory instance
global_ledger = EvidenceLedger()
