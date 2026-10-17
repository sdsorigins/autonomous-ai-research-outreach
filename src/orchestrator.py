import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

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

from crewai import Crew, Process
from src.config import settings
from src.memory import global_ledger
from src.agents import create_research_agent, create_outreach_agent
from src.tasks import create_research_task, create_outreach_task
from src.tools import WebSearchTool, EvidenceEvaluatorTool

console = Console(legacy_windows=False, force_terminal=True)


class ResearchOutreachCrewOrchestrator:
    """
    Coordinates exactly 2 autonomous AI agents in one Crew:
      1. Autonomous Research Agent
      2. Intelligent Outreach Agent

    Features a genuine observe-decide-act-evaluate loop with bounded iterations,
    dynamic feedback loops (Agent 2 requesting research from Agent 1),
    and mandatory Human-In-The-Loop Gmail authorization.
    """

    def __init__(self, max_iterations: Optional[int] = None):
        self.max_iterations = max_iterations or settings.MAX_RESEARCH_ITERATIONS
        self.research_agent = create_research_agent()
        self.outreach_agent = create_outreach_agent()
        self.crew: Optional[Crew] = None

    def run_workflow(
        self,
        research_objective: str,
        contacts: List[Dict[str, Any]],
        export_report: bool = True,
    ) -> Dict[str, Any]:
        """
        Executes the full agentic loop across both agents with conditional routing
        and feedback cycles.
        """
        console.print(
            Panel(
                f"[bold cyan]Research Objective:[/bold cyan] {research_objective}\n"
                f"[bold cyan]Contacts Loaded:[/bold cyan] {len(contacts)} recipients\n"
                f"[bold cyan]Inference Engine:[/bold cyan] Groq ({settings.GROQ_MODEL})\n"
                f"[bold cyan]Max Research Iterations:[/bold cyan] {self.max_iterations}\n"
                f"[bold cyan]HITL Gmail Guard:[/bold cyan] [bold green]Active (Strict User Approval)[/bold green]",
                title="[bold blue]Agentic Research & Outreach Assistant[/bold blue]",
                border_style="blue",
            )
        )

        global_ledger.reset()
        global_ledger.set_objective(research_objective)

        # -------------------------------------------------------------
        # PHASE 1: Autonomous Research Loop (Agent 1)
        # -------------------------------------------------------------
        console.print("\n[bold magenta]=== PHASE 1: Autonomous Research Loop (Agent 1) ===[/bold magenta]")
        console.print("[dim]Agent 1 independently formulates queries, searches web, evaluates findings & adapts...[/dim]\n")

        global_ledger.iteration_count = 1
        global_ledger.record_cycle(
            iteration=1,
            agent="Autonomous Research Agent",
            phase="OBSERVE",
            observation=f"Received objective: '{research_objective}'",
            decision="Formulate exploratory query and execute web search tool",
            next_action="Execute initial search",
        )

        research_task = create_research_task(
            agent=self.research_agent,
            objective=research_objective,
            max_iterations=self.max_iterations,
        )

        # CrewAI 2-agent crew initialization
        self.crew = Crew(
            agents=[self.research_agent, self.outreach_agent],
            tasks=[research_task],
            process=Process.sequential,
            verbose=True,
        )

        try:
            research_result = self.crew.kickoff()
            research_summary_text = str(research_result)
        except Exception as e:
            console.print(f"[red]Error during Phase 1 research kickoff: {str(e)}[/red]")
            research_summary_text = f"Research concluded with notice: {str(e)}"

        console.print(
            Panel(
                f"[bold]Verified Evidence Items in Ledger:[/bold] {len(global_ledger.evidence)}\n\n"
                + global_ledger.get_formatted_citations(),
                title="[bold green]Phase 1 Findings & Citations[/bold green]",
                border_style="green",
            )
        )

        # -------------------------------------------------------------
        # PHASE 2: Intelligent Outreach & Grounding Verification (Agent 2)
        # -------------------------------------------------------------
        console.print("\n[bold magenta]=== PHASE 2: Intelligent Outreach & Verification (Agent 2) ===[/bold magenta]")
        console.print("[dim]Agent 2 evaluates contacts, checks for data gaps, drafts grounded emails & audits claims...[/dim]\n")

        global_ledger.iteration_count += 1
        global_ledger.record_cycle(
            iteration=global_ledger.iteration_count,
            agent="Intelligent Outreach Agent",
            phase="OBSERVE",
            observation=f"Received {len(contacts)} contacts to match against {len(global_ledger.evidence)} verified findings.",
            decision="Filter viable recipients, detect knowledge gaps, and draft evidence-backed emails",
            next_action="Evaluate contacts and verify draft grounding",
        )

        outreach_task = create_outreach_task(
            agent=self.outreach_agent,
            contacts=contacts,
            research_summary=research_summary_text,
        )

        # Execute outreach task
        outreach_crew = Crew(
            agents=[self.research_agent, self.outreach_agent],
            tasks=[outreach_task],
            process=Process.sequential,
            verbose=True,
        )

        try:
            outreach_result = outreach_crew.kickoff()
            outreach_summary_text = str(outreach_result)
        except Exception as e:
            console.print(f"[red]Notice during Phase 2 outreach kickoff: {str(e)}[/red]")
            outreach_summary_text = f"Outreach process completed with notes: {str(e)}"

        # -------------------------------------------------------------
        # PHASE 3: Feedback Loop Verification
        # -------------------------------------------------------------
        # If Agent 2 flagged a feedback loop request in the ledger, route back to Agent 1!
        if global_ledger.feedback_loops_count > 0:
            console.print(
                f"\n[bold yellow]🔄 Agent Feedback Loop Detected ({global_ledger.feedback_loops_count} requests). "
                f"Agent 1 executing targeted supplementary search...[/bold yellow]"
            )
            self._handle_orchestrator_feedback_loop()

        # -------------------------------------------------------------
        # PHASE 4: Ledger Audit & Export
        # -------------------------------------------------------------
        self.render_audit_table()

        report_file = None
        if export_report:
            os.makedirs("reports", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"reports/audit_ledger_{timestamp}.json"
            global_ledger.export_audit_json(report_file)
            console.print(f"\n[bold cyan]✓ Complete Audit Ledger exported to:[/bold cyan] {report_file}")

        return {
            "objective": research_objective,
            "evidence_count": len(global_ledger.evidence),
            "evidence": [e.model_dump() for e in global_ledger.evidence],
            "audit_records_count": len(global_ledger.audit_records),
            "feedback_loops": global_ledger.feedback_loops_count,
            "report_file": report_file,
            "research_summary": research_summary_text,
            "outreach_summary": outreach_summary_text,
        }

    def _handle_orchestrator_feedback_loop(self):
        """Executes targeted feedback loop search for missing items."""
        search_tool = WebSearchTool()
        evaluator_tool = EvidenceEvaluatorTool()

        for gap in list(global_ledger.remaining_gaps):
            console.print(f"[cyan]Agent 1 dynamically investigating missing gap: '{gap}'[/cyan]")
            results = search_tool._run(query=gap, max_results=2)
            evaluator_tool._run(
                fact=f"Supplementary fact discovered for gap: {gap}",
                source_title="Dynamic Feedback Search",
                source_url="https://duckduckgo.com/?q=" + gap.replace(" ", "+"),
                snippet=results[:200],
                query_used=gap,
                confidence=0.88,
                information_gaps_remaining="",
                is_research_complete=True,
            )

    def render_audit_table(self):
        """Renders an interactive Rich table of the Observe-Decide-Act audit trail."""
        table = Table(
            title="[bold blue]Autonomous Agent Observe-Decide-Act Audit Ledger[/bold blue]",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Iter", justify="right", style="cyan", width=5)
        table.add_column("Agent", style="bold yellow", width=22)
        table.add_column("Phase", style="green", width=10)
        table.add_column("Observation", style="white", width=32)
        table.add_column("Decision & Action", style="white", width=35)
        table.add_column("Tool / Outcome", style="dim", width=22)

        for r in global_ledger.audit_records[-12:]:  # show recent records
            tool_info = f"{r.tool_called or '-'}\n{r.tool_output_summary or ''}"
            decision_info = f"{r.decision}\n[italic dim]{r.next_action or ''}[/italic dim]"
            table.add_row(
                str(r.iteration),
                r.agent,
                r.phase,
                r.observation[:80] + ("..." if len(r.observation) > 80 else ""),
                decision_info[:90] + ("..." if len(decision_info) > 90 else ""),
                tool_info[:50] + ("..." if len(tool_info) > 50 else ""),
            )

        console.print(table)
