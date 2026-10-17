import pytest
from src.memory import global_ledger
from src.tools.search_tool import WebSearchTool
from src.tools.evidence_tool import EvidenceEvaluatorTool


def test_evidence_registration_and_citations():
    global_ledger.reset()

    evaluator = EvidenceEvaluatorTool()
    result = evaluator._run(
        fact="Agentic workflows achieve 4x throughput gains in enterprise tests.",
        source_title="AI Systems Journal 2026",
        source_url="https://example.com/ai-systems-2026",
        snippet="In rigorous enterprise testing, agentic workflows delivered 4x throughput gains.",
        query_used="agentic workflow enterprise throughput gains 2026",
        confidence=0.94,
        information_gaps_remaining="latency trade-offs",
        is_research_complete=False,
    )

    assert "SUCCESS: Recorded [E1]" in result
    assert len(global_ledger.evidence) == 1
    assert global_ledger.evidence[0].id == "[E1]"
    assert global_ledger.evidence[0].confidence == 0.94
    assert "latency trade-offs" in global_ledger.remaining_gaps

    citations = global_ledger.get_formatted_citations()
    assert "[E1]" in citations
    assert "https://example.com/ai-systems-2026" in citations


def test_web_search_tool_execution():
    tool = WebSearchTool()
    output = tool._run(query="Python CrewAI Groq multi-agent", max_results=2)
    assert isinstance(output, str)
    assert len(output) > 20
    # Should contain either results or observation notes or exception handling
    out_lower = output.lower()
    assert "observation:" in out_lower or "title:" in out_lower or "exception" in out_lower
