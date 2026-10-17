import json
from typing import List, Dict, Any
from crewai import Task, Agent


def create_research_task(agent: Agent, objective: str, max_iterations: int = 3) -> Task:
    """
    Creates the autonomous research task for Agent 1.
    """
    description = (
        f"RESEARCH OBJECTIVE: {objective}\n\n"
        f"INSTRUCTIONS FOR AUTONOMOUS INVESTIGATION:\n"
        f"1. OBSERVE & PLAN: Formulate your initial search query based on the objective.\n"
        f"2. ACT: Execute the query using the 'Live Web Search' tool.\n"
        f"3. EVALUATE: Analyze the search snippets carefully. Identify what facts were verified and "
        f"what information gaps remain.\n"
        f"4. ADAPT STRATEGY: If results are too broad, ambiguous, or missing crucial details, DO NOT stop. "
        f"Formulate a refined, targeted follow-up query and execute another search.\n"
        f"5. RECORD: For every verified finding, call the 'Evidence Evaluator & Ledger' tool to store the fact, "
        f"source title, URL, and snippet.\n"
        f"6. STOPPING CONDITION: You must stop searching once you have gathered sufficient high-confidence evidence "
        f"or reached a maximum of {max_iterations} search iterations.\n\n"
        f"FINAL DELIVERABLE:\n"
        f"- A structured intelligence summary synthesizing key facts.\n"
        f"- Explicit list of verified evidence with citation tags [E1], [E2], etc.\n"
        f"- Any remaining unanswered questions or identified gaps."
    )

    expected_output = (
        "A comprehensive, source-cited research brief containing verified claims, "
        "citation IDs [E1], [E2] mapped to sources, and an assessment of evidence completeness."
    )

    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
    )


def create_outreach_task(
    agent: Agent,
    contacts: List[Dict[str, Any]],
    research_summary: str = "",
) -> Task:
    """
    Creates the intelligent outreach and claim-verification task for Agent 2.
    """
    contacts_formatted = json.dumps(contacts, indent=2)

    description = (
        f"CONTACT LIST TO EVALUATE:\n{contacts_formatted}\n\n"
        f"RESEARCH CONTEXT AVAILABLE:\n{research_summary or 'Consult the shared Evidence Ledger.'}\n\n"
        f"INSTRUCTIONS FOR INTELLIGENT OUTREACH:\n"
        f"1. EVALUATE CONTACTS: Review each contact in the list. Evaluate relevance against the research objective.\n"
        f"   - Categorize each as SUITABLE or UNSUITABLE.\n"
        f"   - Provide clear, explicit rationale explaining why they were chosen or excluded.\n"
        f"2. IDENTIFY RESEARCH GAPS: For suitable contacts, determine if essential information is missing to craft "
        f"an impactful pitch. If critical facts are absent, invoke 'Request Additional Research' to request data from Agent 1.\n"
        f"3. DRAFT PERSONALIZED OUTREACH: For each approved recipient, write a customized email.\n"
        f"   - Directly connect their role/interests to specific verified facts from the research findings.\n"
        f"   - Embed exact evidence citations [E1], [E2] for every factual statement.\n"
        f"4. CLAIM AUDIT: Invoke the 'Claim & Hallucination Verifier' tool on your draft to check grounding.\n"
        f"   - If any claim is flagged as UNSUPPORTED, edit the draft immediately to remove or rectify it.\n"
        f"5. HUMAN-IN-THE-LOOP APPROVAL: For verified drafts, invoke the 'Gmail Outreach Dispatcher' tool.\n"
        f"   - This triggers the mandatory interactive user approval prompt.\n"
        f"   - Respect the human decision (Approve, Edit, Dry-Run, or Reject).\n\n"
        f"FINAL DELIVERABLE:\n"
        f"- Full report of contact evaluations (with acceptance/rejection reasoning).\n"
        f"- Claim verification audit results.\n"
        f"- Final status of each email (Sent, Dry-Run, Edited, or Skipped)."
    )

    expected_output = (
        "A complete outreach campaign report detailing contact selection decisions, "
        "grounding audit scores, finalized email texts, and user authorization outcomes."
    )

    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
    )
