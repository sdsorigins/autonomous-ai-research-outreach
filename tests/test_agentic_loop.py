import os
import pytest
from src.memory import global_ledger
from src.agents import (
    create_research_agent,
    create_data_analyst_agent,
    create_verification_agent,
    create_outreach_agent,
)
from crewai import LLM


def test_agent_initialization_with_tools():
    test_llm = LLM(model="groq/llama-3.3-70b-versatile", api_key="test_key")

    agent_1 = create_research_agent(llm=test_llm)
    agent_2 = create_data_analyst_agent(llm=test_llm)
    agent_3 = create_verification_agent(llm=test_llm)
    agent_4 = create_outreach_agent(llm=test_llm)

    assert agent_1.role == "Senior Research Strategist"
    assert len(agent_1.tools) == 2
    tool_names_1 = [t.name for t in agent_1.tools]
    assert "Live Web Search" in tool_names_1
    assert "Evidence Evaluator & Ledger" in tool_names_1

    assert agent_2.role == "Quantitative & Statistical Analyst"
    assert len(agent_2.tools) == 1
    assert agent_2.tools[0].name == "Evidence Evaluator & Ledger"

    assert agent_3.role == "Chief Citations & Forensic Fact Verifier"
    assert len(agent_3.tools) == 2
    tool_names_3 = [t.name for t in agent_3.tools]
    assert "Claim & Hallucination Verifier" in tool_names_3
    assert "Request Additional Research" in tool_names_3

    assert agent_4.role == "Executive Synthesis & Delivery Specialist"
    assert len(agent_4.tools) == 2


def test_audit_ledger_observe_decide_act_export():
    global_ledger.reset()
    global_ledger.set_objective("Evaluate enterprise AI reliability")

    global_ledger.record_cycle(
        iteration=1,
        agent="Autonomous Research Agent",
        phase="OBSERVE",
        observation="Search query returned 3 results",
        decision="Filter verified metrics",
        tool_called="Live Web Search",
        tool_input={"query": "test"},
        tool_output_summary="3 results",
        evaluation="Sufficient",
        next_action="Register findings",
    )

    trail = global_ledger.get_audit_trail()
    assert len(trail) == 1
    assert trail[0].phase == "OBSERVE"
    assert trail[0].agent == "Autonomous Research Agent"

    os.makedirs("reports", exist_ok=True)
    report_file = "reports/test_audit_export.json"
    global_ledger.export_audit_json(report_file)

    assert os.path.exists(report_file)
