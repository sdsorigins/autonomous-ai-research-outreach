import os
import sys
import json
import argparse
from pathlib import Path

# Ensure UTF-8 console encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from src.config import settings
from src.memory import global_ledger
from src.orchestrator import ResearchOutreachCrewOrchestrator
from src.demo import run_interactive_demonstration

console = Console(legacy_windows=False, force_terminal=True)


def print_banner():
    banner_text = (
        "[bold cyan]Agentic AI Research & Outreach Assistant[/bold cyan]\n"
        "[white]Two Autonomous Agents in One Crew with Groq, DuckDuckGo & Gmail API[/white]\n"
        "[dim]Featuring Observe-Decide-Act Loops, Adaptive Search, Grounding Audits, and Human-In-The-Loop Guards[/dim]"
    )
    console.print(Panel(banner_text, border_style="cyan", padding=(1, 2)))


def load_contacts(contacts_file: str) -> list:
    path = Path(contacts_file)
    if not path.exists():
        console.print(f"[yellow]Contacts file '{contacts_file}' not found. Using default dataset.[/yellow]")
        path = Path("data/contacts.json")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def handle_live_workflow(objective: str = "", contacts_file: str = "data/contacts.json"):
    print_banner()

    # Check Groq configuration
    if not settings.is_groq_configured():
        console.print("\n[bold yellow]⚠️ Groq API Key Not Configured[/bold yellow]")
        console.print(
            "To execute live inference with Groq, set your [cyan]GROQ_API_KEY[/cyan] in [cyan].env[/cyan].\n"
            "Free keys are available at: [link=https://console.groq.com]https://console.groq.com[/link]\n"
        )
        run_demo = Confirm.ask("Would you like to run the interactive tool-adaptation demonstration instead?", default=True)
        if run_demo:
            run_interactive_demonstration(interactive=True)
            return
        else:
            console.print("[red]Operation cancelled. Please update .env and try again.[/red]")
            return

    if not objective:
        objective = Prompt.ask(
            "\n[bold]Enter your Research Objective[/bold]",
            default="Investigate breakthroughs in agentic AI memory and tool-use orchestration in 2026",
        )

    contacts = load_contacts(contacts_file)
    console.print(f"[green]Loaded {len(contacts)} contacts from {contacts_file}[/green]")

    orchestrator = ResearchOutreachCrewOrchestrator()
    orchestrator.run_workflow(
        research_objective=objective,
        contacts=contacts,
        export_report=True,
    )


def handle_view_reports():
    reports_dir = Path("reports")
    if not reports_dir.exists():
        console.print("[yellow]No reports directory found yet.[/yellow]")
        return

    json_files = list(reports_dir.glob("audit_ledger_*.json"))
    if not json_files:
        console.print("[yellow]No audit ledger files found in reports/.[/yellow]")
        return

    console.print(f"\n[bold green]Found {len(json_files)} audit ledger reports:[/bold green]")
    for idx, f in enumerate(json_files, 1):
        console.print(f"  [{idx}] {f.name} ({f.stat().st_size} bytes)")

    selection = Prompt.ask("\nEnter report number to view (or press Enter to skip)", default="")
    if selection.isdigit() and 1 <= int(selection) <= len(json_files):
        selected_file = json_files[int(selection) - 1]
        with open(selected_file, "r", encoding="utf-8") as rf:
            data = json.load(rf)
            console.print(Panel(json.dumps(data, indent=2)[:2000] + "\n...", title=f"Report: {selected_file.name}"))


def interactive_menu():
    while True:
        print_banner()
        console.print("[bold]Select an action:[/bold]")
        console.print("  [bold green][1][/bold green] Run Live Autonomous Crew (Groq + DuckDuckGo + Gmail HITL)")
        console.print("  [bold cyan][2][/bold cyan] Run Tool Adaptation & Feedback Demonstration (Observe-Decide-Act)")
        console.print("  [bold yellow][3][/bold yellow] Run Test Suite (pytest)")
        console.print("  [bold magenta][4][/bold magenta] View Exported Audit Ledgers")
        console.print("  [bold red][5][/bold red] Exit")

        choice = Prompt.ask("\nEnter choice", choices=["1", "2", "3", "4", "5"], default="2")

        if choice == "1":
            handle_live_workflow()
        elif choice == "2":
            run_interactive_demonstration(interactive=True)
        elif choice == "3":
            os.system(f"{sys.executable} -m pytest tests/ -v")
        elif choice == "4":
            handle_view_reports()
        elif choice == "5":
            console.print("[green]Goodbye![/green]")
            break

        Prompt.ask("\n[dim]Press Enter to return to main menu...[/dim]", default="")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Agentic AI Research and Outreach Assistant (CrewAI + Groq API)"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run the step-by-step tool adaptation and feedback demonstration",
    )
    parser.add_argument(
        "--objective",
        type=str,
        default="",
        help="Specify the research objective directly via CLI",
    )
    parser.add_argument(
        "--contacts",
        type=str,
        default="data/contacts.json",
        help="Path to JSON contacts list",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run in non-interactive batch mode (auto dry-run)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.demo:
        run_interactive_demonstration(interactive=not args.non_interactive)
    elif args.objective:
        handle_live_workflow(objective=args.objective, contacts_file=args.contacts)
    else:
        interactive_menu()
