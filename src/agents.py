from typing import Optional
from crewai import Agent, LLM
from src.config import settings
from src.tools import (
    WebSearchTool,
    EvidenceEvaluatorTool,
    ClaimVerifierTool,
    RequestMoreResearchTool,
    GmailOutreachTool,
)


def create_research_agent(llm: Optional[LLM] = None) -> Agent:
    """
    Agent 1 — Senior Research Strategist
    Formulates hypotheses, conducts targeted live web investigations,
    identifies knowledge gaps, and gathers primary factual evidence.
    """
    active_llm = llm or settings.get_llm()

    return Agent(
        role="Senior Research Strategist",
        goal=(
            "Independently investigate the provided research objective using dynamic web search. "
            "Formulate strategic queries, evaluate source relevance, log empirical findings into the "
            "Evidence Ledger with exact source URLs, and adapt search terms when encountering ambiguity."
        ),
        backstory=(
            "You are a principal investigative researcher with deep expertise in technology intelligence. "
            "You operate methodically, formulating hypotheses and querying primary documentation to unearth "
            "empirical data rather than speculative commentary."
        ),
        tools=[WebSearchTool(), EvidenceEvaluatorTool()],
        llm=active_llm,
        verbose=True,
        memory=False,
        max_iter=settings.MAX_RESEARCH_ITERATIONS * 3,
        allow_delegation=False,
    )


def create_data_analyst_agent(llm: Optional[LLM] = None) -> Agent:
    """
    Agent 2 — Quantitative & Statistical Analyst
    Isolates hard numbers, benchmarks, percentages, comparative metrics,
    and structures findings into tabular statistical datasets.
    """
    active_llm = llm or settings.get_llm()

    return Agent(
        role="Quantitative & Statistical Analyst",
        goal=(
            "Extract quantifiable metrics, performance benchmarks, growth rates, and statistical points "
            "from raw research data. Structure these into clear comparative tabular formats for executive analysis."
        ),
        backstory=(
            "You are a quantitative data scientist and market intelligence analyst. You focus strictly on numbers, "
            "percentages, throughput rates, and comparative statistics. You turn unstructured findings into "
            "rigorous, standardized data tables."
        ),
        tools=[EvidenceEvaluatorTool()],
        llm=active_llm,
        verbose=True,
        memory=False,
        max_iter=6,
        allow_delegation=False,
    )


def create_verification_agent(llm: Optional[LLM] = None) -> Agent:
    """
    Agent 3 — Citations & Forensic Fact Verifier
    Scrutinizes claims word-for-word against the Evidence Ledger, verifies canonical URLs,
    eliminates ungrounded statements, and certifies the Grounding Score.
    """
    active_llm = llm or settings.get_llm()

    return Agent(
        role="Chief Citations & Forensic Fact Verifier",
        goal=(
            "Rigorously audit all synthesized claims and statistical figures. Cross-reference every assertion "
            "against source citations [E1], [E2], detect any hallucinations, and certify the evidentiary grounding score."
        ),
        backstory=(
            "You are a forensic verification officer with a zero-tolerance policy for unsubstantiated claims. "
            "Every metric and conclusion must map to an empirical source citation, ensuring bulletproof reporting integrity."
        ),
        tools=[ClaimVerifierTool(), RequestMoreResearchTool()],
        llm=active_llm,
        verbose=True,
        memory=False,
        max_iter=6,
        allow_delegation=False,
    )


def create_outreach_agent(llm: Optional[LLM] = None) -> Agent:
    """
    Agent 4 — Executive Synthesis & Delivery Specialist
    Synthesizes findings and statistical tables into an executive-ready brief,
    prepares the PDF report, and formats tailored stakeholder communication.
    """
    active_llm = llm or settings.get_llm()

    return Agent(
        role="Executive Synthesis & Delivery Specialist",
        goal=(
            "Compile verified research findings and statistical tables into an authoritative, executive-ready summary. "
            "Draft concise stakeholder outreach and assemble the formal PDF intelligence report."
        ),
        backstory=(
            "You are an executive communications director who drafts crisp, dignified briefings for enterprise leadership. "
            "You communicate with clarity, precision, and zero fluff, organizing complex findings into actionable intelligence."
        ),
        tools=[ClaimVerifierTool(), GmailOutreachTool()],
        llm=active_llm,
        verbose=True,
        memory=False,
        max_iter=6,
        allow_delegation=False,
    )
