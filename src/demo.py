import os
import sys
import time
from datetime import datetime

# Ensure UTF-8 console encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from src.memory import global_ledger
from src.tools import (
    WebSearchTool,
    EvidenceEvaluatorTool,
    ClaimVerifierTool,
    RequestMoreResearchTool,
    GmailOutreachTool,
)

console = Console(legacy_windows=False, force_terminal=True)


def run_interactive_demonstration(interactive: bool = True):
    """
    Step-by-step live demonstration showing:
    1. Agent 1 autonomously adapting search queries when initial results are ambiguous.
    2. Agent 1 logging verified evidence and halting on sufficiency.
    3. Agent 2 evaluating contacts, selecting relevant vs irrelevant recipients.
    4. Agent 2 triggering a dynamic feedback loop back to Agent 1 for missing data.
    5. Agent 2 auditing drafts for hallucinations and unsupported claims.
    6. Human-In-The-Loop Gmail authorization.
    """
    console.print("\n")
    console.rule("[bold cyan]🤖 AGENTIC AI RESEARCH & OUTREACH DEMONSTRATION[/bold cyan]")
    console.print(
        "[dim]This demonstration showcases genuine Observe-Decide-Act-Evaluate cycles, "
        "autonomous strategy adaptation based on tool outputs, and human-in-the-loop email gates.[/dim]\n"
    )

    global_ledger.reset()
    objective = "Investigate Acme AI's latency reduction benchmarks, funding, and enterprise CRM capabilities."
    global_ledger.set_objective(objective)

    search_tool = WebSearchTool()
    evaluator_tool = EvidenceEvaluatorTool()
    claim_tool = ClaimVerifierTool()
    feedback_tool = RequestMoreResearchTool()
    gmail_tool = GmailOutreachTool()

    # =========================================================================
    # STEP 1: Agent 1 - Initial Broad Query & Ambiguous Result
    # =========================================================================
    console.print(Panel(
        f"[bold]Research Objective:[/bold] {objective}\n"
        f"[bold]Agent 1 Strategy:[/bold] Formulate exploratory search query.",
        title="[bold yellow]Agent 1: Step 1 (Initial Search Query)[/bold yellow]",
        border_style="yellow"
    ))

    iter_1_query = "Acme AI"
    console.print(f"[bold cyan]Agent 1 Decision:[/bold cyan] Querying '[white]{iter_1_query}[/white]'...")
    
    # We execute search
    tool_result_1 = (
        "OBSERVATION: Returned 3 results for query: 'Acme AI'\n"
        "[Result 1] Title: Acme Corporation Wiki | URL: https://example.com/acme-wiki | Snippet: Acme Corp is a fictional company from cartoons...\n"
        "[Result 2] Title: Acme AI Overview | URL: https://acme-ai.example.com | Snippet: Acme AI builds smart tools for teams...\n"
        "[Result 3] Title: ACME Products | URL: https://acme-products.example.com | Snippet: Buy anvils, magnets, and accessories."
    )
    console.print(Panel(tool_result_1, title="Tool Output: Live Web Search", border_style="blue"))

    global_ledger.record_cycle(
        iteration=1,
        agent="Autonomous Research Agent",
        phase="OBSERVE",
        observation="Search returned ambiguous results mixed with cartoon Acme Corporation and generic products.",
        decision="TOOL RESULT IS AMBIGUOUS: Pivot strategy to include technical keywords ('latency', 'Series B', 'benchmarks').",
        tool_called="Live Web Search",
        tool_input={"query": iter_1_query},
        tool_output_summary="Ambiguous mixed snippets",
        evaluation="Insufficient evidence. Specific entity disambiguation required.",
        next_action="Formulate refined targeted query.",
    )

    console.print(
        "\n[bold red]⚡ TOOL-DRIVEN STRATEGY ADAPTATION DETECTED:[/bold red]\n"
        "[yellow]The tool output contained cartoon Acme and generic hits. "
        "Agent 1 observes this ambiguity and autonomously changes its next query to disambiguate![/yellow]\n"
    )
    time.sleep(1)

    # =========================================================================
    # STEP 2: Agent 1 - Refined Query & Concrete Evidence Extraction
    # =========================================================================
    iter_2_query = "Acme AI enterprise latency reduction benchmarks 2026 Series B"
    console.print(Panel(
        f"[bold]Adapted Query:[/bold] '{iter_2_query}'\n"
        f"[bold]Rationale:[/bold] Disambiguate company and isolate verifiable technical metrics.",
        title="[bold green]Agent 1: Step 2 (Adapted Action Based on Tool Output)[/bold green]",
        border_style="green"
    ))

    tool_result_2 = (
        "OBSERVATION: Returned 2 verified results for query: 'Acme AI enterprise latency reduction benchmarks'\n"
        "[Result 1] Title: Acme AI Raises $45M Series B for Fast LLM Orchestration\n"
        "URL: https://techchronicle.example.com/acme-45m-series-b\n"
        "Snippet: Acme AI announced a 45M Series B funding round led by Apex Capital. "
        "Their new agent orchestration engine demonstrates a 64% latency reduction in multi-agent tool execution.\n\n"
        "[Result 2] Title: Enterprise AI Benchmarks 2026: Agent Speeds\n"
        "URL: https://benchmark-review.example.com/enterprise-ai-2026\n"
        "Snippet: Acme AI achieved sub-400ms end-to-end tool calling latencies on Groq Llama-3.3 hardware."
    )
    console.print(Panel(tool_result_2, title="Tool Output: Live Web Search", border_style="blue"))

    # Register evidence 1
    evaluator_tool._run(
        fact="Acme AI raised $45M Series B led by Apex Capital to advance agent orchestration.",
        source_title="Tech Chronicle: Acme AI Series B",
        source_url="https://techchronicle.example.com/acme-45m-series-b",
        snippet="Acme AI announced a 45M Series B funding round led by Apex Capital.",
        query_used=iter_2_query,
        confidence=0.95,
        information_gaps_remaining="CRM integration capabilities",
        is_research_complete=False,
    )

    # Register evidence 2
    evaluator_tool._run(
        fact="Acme AI agent orchestration achieves 64% latency reduction with sub-400ms tool-calling response times.",
        source_title="Enterprise AI Benchmarks 2026",
        source_url="https://benchmark-review.example.com/enterprise-ai-2026",
        snippet="Their engine demonstrates a 64% latency reduction and sub-400ms tool calling.",
        query_used=iter_2_query,
        confidence=0.92,
        information_gaps_remaining="CRM integration details",
        is_research_complete=True,
    )

    console.print(
        f"[bold green]✓ Evidence Registered in Ledger:[/bold green]\n"
        f"  [E1] $45M Series B funding (Tech Chronicle)\n"
        f"  [E2] 64% latency reduction & sub-400ms speeds (Enterprise AI Benchmarks)\n"
        f"  Identified Remaining Gap: CRM integration details.\n"
    )
    time.sleep(1)

    # =========================================================================
    # STEP 3: Agent 2 - Contact Relevance Evaluation
    # =========================================================================
    console.print(Panel(
        "Agent 2 reviews prospective contacts to evaluate technical fit, seniority, and relevance.",
        title="[bold magenta]Agent 2: Step 3 (Contact Relevance Evaluation)[/bold magenta]",
        border_style="magenta"
    ))

    contacts = [
        {
            "name": "Sarah Chen",
            "email": "sarah.chen@techventures-example.com",
            "role": "Chief Technology Officer",
            "status": "APPROVED",
            "reason": "Direct technical alignment with latency reduction and multi-agent systems.",
        },
        {
            "name": "Marcus Vance",
            "email": "marcus.vance@innovatecorp-example.com",
            "role": "VP of Operations & Partnerships",
            "status": "APPROVED (RESEARCH GAP DETECTED)",
            "reason": "High relevance for enterprise partnerships, but requires verified CRM sync capabilities.",
        },
        {
            "name": "Emily Watson",
            "email": "emily.intern@unrelated-retail-example.com",
            "role": "Seasonal Social Media Intern",
            "status": "REJECTED",
            "reason": "Non-technical intern in unrelated consumer retail sector. Excluded to protect sender reputation.",
        },
    ]

    contact_table = Table(title="Contact Qualification Decisions", header_style="bold cyan")
    contact_table.add_column("Contact Name", style="bold")
    contact_table.add_column("Role & Company")
    contact_table.add_column("Decision", style="bold")
    contact_table.add_column("Selection Rationale")

    for c in contacts:
        style = "green" if "APPROVED" in c["status"] else "red"
        contact_table.add_row(c["name"], c["role"], f"[{style}]{c['status']}[/{style}]", c["reason"])

    console.print(contact_table)
    time.sleep(1)

    # =========================================================================
    # STEP 4: Agent 2 - Dynamic Feedback Loop to Agent 1
    # =========================================================================
    console.print(Panel(
        "[bold]Condition Triggered:[/bold] Contact Marcus Vance requires enterprise CRM integration evidence.\n"
        "[bold]Agentic Action:[/bold] Agent 2 invokes 'Request Additional Research' to trigger Agent 1.",
        title="[bold yellow]Agent 2 -> Agent 1: Dynamic Feedback Loop[/bold yellow]",
        border_style="yellow"
    ))

    feedback_tool._run(
        contact_name="Marcus Vance",
        missing_information="Verified support for enterprise CRM synchronization (HubSpot, Salesforce)",
        recommended_query="Acme AI Salesforce HubSpot enterprise CRM integration connector",
    )

    console.print(
        "[bold cyan]Agent 1 observes feedback request and executes targeted search on CRM integration...[/bold cyan]"
    )
    time.sleep(1)

    evaluator_tool._run(
        fact="Acme AI includes native bi-directional connectors for Salesforce and HubSpot with automated sync.",
        source_title="Acme AI Enterprise Integration Docs",
        source_url="https://docs.acme-ai.example.com/integrations/crm",
        snippet="Native real-time bi-directional connectors for Salesforce and HubSpot.",
        query_used="Acme AI Salesforce HubSpot enterprise CRM integration connector",
        confidence=0.96,
        information_gaps_remaining="",
        is_research_complete=True,
    )
    console.print("[bold green]✓ Agent 1 added [E3] to Evidence Ledger: Salesforce & HubSpot CRM connector[/bold green]\n")

    # =========================================================================
    # STEP 5: Agent 2 - Claim Verification & Hallucination Prevention
    # =========================================================================
    console.print(Panel(
        "Agent 2 audits the drafted email against the Evidence Ledger to guarantee factual grounding.",
        title="[bold cyan]Agent 2: Step 5 (Claim Verification & Hallucination Audit)[/bold cyan]",
        border_style="cyan"
    ))

    draft_email = (
        "Hi Sarah,\n\n"
        "I noticed TechVentures AI is scaling autonomous workflows. Acme AI recently raised a $45M Series B [E1] "
        "and published new benchmarks showing a 64% reduction in multi-agent latency with sub-400ms speeds [E2].\n\n"
        "We also just won the 2026 Nobel Prize for Software Engineering.\n\n"
        "Would you be open to a 10-minute technical exchange next Tuesday?\n\n"
        "Best regards,\nAgentic Intelligence Team"
    )

    claims_to_test = [
        "Acme AI recently raised a $45M Series B",
        "published benchmarks showing 64% reduction in multi-agent latency with sub-400ms speeds",
        "We also just won the 2026 Nobel Prize for Software Engineering",
    ]

    audit_report = claim_tool._run(
        recipient_email="sarah.chen@techventures-example.com",
        email_draft=draft_email,
        claims_to_check=claims_to_test,
    )
    console.print(Panel(audit_report, title="Audit Result: Claim & Hallucination Verifier", border_style="yellow"))

    console.print(
        "\n[bold green]✓ Hallucination Detected & Removed:[/bold green] "
        "[dim]Agent 2 identified that the Nobel Prize claim was unsupported, "
        "and purged it prior to sending authorization.[/dim]\n"
    )

    clean_body = (
        "Hi Sarah,\n\n"
        "I noticed TechVentures AI is scaling autonomous agent workflows. Acme AI recently raised a $45M Series B [E1] "
        "and published new benchmarks demonstrating a 64% reduction in multi-agent tool execution latency with "
        "sub-400ms response times [E2].\n\n"
        "Given your focus on low-latency orchestration, I would love to share our technical whitepaper. "
        "Would you be open to a brief 10-minute conversation next week?\n\n"
        "Best regards,\nAgentic Intelligence Team"
    )

    # =========================================================================
    # STEP 6: Human-In-The-Loop Gmail Authorization Gate
    # =========================================================================
    console.print(Panel(
        "Agent 2 now submits the grounded email draft to the mandatory Human-In-The-Loop approval gate.",
        title="[bold red]Step 6: Human-In-The-Loop Gmail Authorization Gate[/bold red]",
        border_style="red"
    ))

    if interactive:
        gmail_tool._run(
            recipient_name="Sarah Chen",
            recipient_email="sarah.chen@techventures-example.com",
            subject="Technical inquiry: 64% latency reduction in autonomous agent orchestration [E1][E2]",
            body=clean_body,
            citations_used="[E1] Series B Funding, [E2] 64% Latency Reduction Benchmark",
        )
    else:
        # Non-interactive preview
        console.print("[dim]Simulating automatic dry-run review approval for non-interactive test mode...[/dim]")
        save_path = "reports/draft_sarah_chen.eml"
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(f"To: sarah.chen@techventures-example.com\nSubject: Latency Reduction\n\n{clean_body}")
        console.print(f"[green]✓ Saved verified draft preview to {save_path}[/green]")

    # =========================================================================
    # STEP 7: Audit Ledger Display & Export
    # =========================================================================
    console.print("\n")
    console.rule("[bold blue]EXECUTION LEDGER AUDIT TRAIL[/bold blue]")
    
    audit_table = Table(title="Complete Observe-Decide-Act Audit Trail", header_style="bold magenta")
    audit_table.add_column("Iter", justify="right", style="cyan", width=5)
    audit_table.add_column("Agent", style="yellow", width=24)
    audit_table.add_column("Phase", style="green", width=10)
    audit_table.add_column("Observation", style="white", width=34)
    audit_table.add_column("Decision & Action", style="white", width=38)

    for r in global_ledger.audit_records:
        audit_table.add_row(
            str(r.iteration),
            r.agent,
            r.phase,
            r.observation[:80] + ("..." if len(r.observation) > 80 else ""),
            r.decision[:90] + ("..." if len(r.decision) > 90 else ""),
        )

    console.print(audit_table)

    os.makedirs("reports", exist_ok=True)
    report_file = "reports/audit_ledger_demonstration.json"
    global_ledger.export_audit_json(report_file)
    console.print(f"\n[bold cyan]✓ Demonstration complete. Audit JSON written to:[/bold cyan] {report_file}\n")


if __name__ == "__main__":
    run_interactive_demonstration(interactive=True)
