import os
import sys
import base64
from email.mime.text import MIMEText
from typing import Type, Optional, Tuple

# Ensure UTF-8 console encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from src.config import settings
from src.memory import global_ledger

console = Console(legacy_windows=False, force_terminal=True)


class SendEmailInput(BaseModel):
    recipient_name: str = Field(description="Name of recipient")
    recipient_email: str = Field(description="Email address of recipient")
    subject: str = Field(description="Personalized email subject line")
    body: str = Field(description="Full personalized email body content grounded in research")
    citations_used: str = Field(
        default="",
        description="Comma-separated evidence IDs used e.g. '[E1], [E2]'"
    )


class GmailApprovalManager:
    """
    Enforces strict Human-In-The-Loop (HITL) authorization for all email dispatches.
    Under NO CIRCUMSTANCES can an email be sent without explicit user confirmation.
    """

    @staticmethod
    def prompt_user_for_approval(
        recipient_name: str,
        recipient_email: str,
        subject: str,
        body: str,
        citations: str,
    ) -> Tuple[str, str, str]:
        """
        Presents the interactive terminal approval modal.
        Returns: (decision_status, final_subject, final_body)
        decision_status can be: 'APPROVED', 'EDITED', 'DRY_RUN', 'REJECTED'
        """
        console.print("\n")
        console.rule("[bold red]🚨 HUMAN-IN-THE-LOOP APPROVAL REQUIRED 🚨[/bold red]")
        console.print(
            "[yellow]The agent has prepared an outreach email grounded in research. "
            "Policy strictly prohibits automatic sending. Please review and authorize:[/yellow]\n"
        )

        preview_content = (
            f"[bold cyan]Recipient:[/bold cyan] {recipient_name} <{recipient_email}>\n"
            f"[bold cyan]Subject:[/bold cyan] {subject}\n"
            f"[bold cyan]Grounded Citations:[/bold cyan] {citations or 'None specified'}\n\n"
            f"[bold cyan]Message Body:[/bold cyan]\n"
            f"{body}"
        )

        console.print(
            Panel(
                preview_content,
                title="[bold green]Outreach Draft Review[/bold green]",
                border_style="green",
            )
        )

        console.print("[bold]Options:[/bold]")
        console.print("  [bold green][A][/bold green] Approve & Send via Gmail API")
        console.print("  [bold yellow][E][/bold yellow] Edit subject or body before sending")
        console.print("  [bold cyan][D][/bold cyan] Dry-Run / Save local draft (do not dispatch live)")
        console.print("  [bold red][R][/bold red] Reject & Skip this email entirely")

        choice = Prompt.ask(
            "\nEnter your decision",
            choices=["A", "a", "E", "e", "D", "d", "R", "r"],
            default="D",
        ).upper()

        if choice == "A":
            return "APPROVED", subject, body
        elif choice == "E":
            console.print("\n[bold yellow]-- Manual Editing Mode --[/bold yellow]")
            new_subject = Prompt.ask("Edit Subject", default=subject)
            console.print("Paste or edit new body (single-line or press Enter to keep):")
            new_body = Prompt.ask("Edit Body", default=body)
            return "EDITED", new_subject, new_body
        elif choice == "D":
            return "DRY_RUN", subject, body
        else:
            return "REJECTED", subject, body


class GmailServiceWrapper:
    """
    Handles Gmail API communication with OAuth 2.0 and graceful dry-run simulation.
    """

    @classmethod
    def get_service(cls):
        """Builds authenticated Gmail API service or None if credentials absent."""
        cred_path = settings.GMAIL_CREDENTIALS_PATH
        token_path = settings.GMAIL_TOKEN_PATH

        if not os.path.exists(cred_path) and not os.path.exists(token_path):
            return None

        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build

            SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
            creds = None

            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                elif os.path.exists(cred_path):
                    flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    return None

                with open(token_path, "w") as token:
                    token.write(creds.to_json())

            return build("gmail", "v1", credentials=creds)
        except Exception as e:
            console.print(f"[yellow]Warning: Gmail API initialization encountered: {e}[/yellow]")
            return None

    @classmethod
    def create_message(cls, to: str, subject: str, body: str) -> dict:
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        return {"raw": raw}


class GmailOutreachTool(BaseTool):
    name: str = "Gmail Outreach Dispatcher"
    description: str = (
        "Prepares and dispatches an outreach email to a verified contact. "
        "MANDATORY REQUIREMENT: This tool triggers a Human-In-The-Loop approval gate. "
        "No email is transmitted to the Gmail API unless explicit human approval is granted."
    )
    args_schema: Type[BaseModel] = SendEmailInput

    def _run(
        self,
        recipient_name: str,
        recipient_email: str,
        subject: str,
        body: str,
        citations_used: str = "",
    ) -> str:
        # Step 1: Enforce mandatory Human-In-The-Loop Approval Gate
        decision, final_subject, final_body = GmailApprovalManager.prompt_user_for_approval(
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            subject=subject,
            body=body,
            citations=citations_used,
        )

        # Step 2: Handle user decision
        if decision == "REJECTED":
            global_ledger.record_cycle(
                iteration=global_ledger.iteration_count,
                agent="Intelligent Outreach Agent",
                phase="ACT",
                observation=f"Email to {recipient_email} rejected by user in HITL review.",
                decision="Cancel transmission",
                tool_called="Gmail Outreach Dispatcher",
                tool_input={"recipient": recipient_email, "subject": subject},
                tool_output_summary="REJECTED_BY_USER",
                evaluation="Email was dismissed by human supervisor.",
                next_action="Move to next contact or complete task.",
            )
            return f"RESULT: User REJECTED sending email to {recipient_name} ({recipient_email}). No message was sent."

        # Prepare message payload
        payload = GmailServiceWrapper.create_message(
            to=recipient_email,
            subject=final_subject,
            body=final_body,
        )

        service = GmailServiceWrapper.get_service()

        if decision in ("APPROVED", "EDITED") and service:
            try:
                sent_msg = service.users().messages().send(userId="me", body=payload).execute()
                msg_id = sent_msg.get("id", "UNKNOWN_ID")
                outcome = f"SUCCESS: Sent email via Gmail API to {recipient_email}. Message ID: {msg_id}"
                
                global_ledger.record_cycle(
                    iteration=global_ledger.iteration_count,
                    agent="Intelligent Outreach Agent",
                    phase="ACT",
                    observation=f"Email sent via Gmail API (ID: {msg_id})",
                    decision="Delivered message",
                    tool_called="Gmail Outreach Dispatcher",
                    tool_input={"recipient": recipient_email, "subject": final_subject},
                    tool_output_summary=f"Sent. Message ID: {msg_id}",
                    evaluation="Delivered with explicit user authorization.",
                    next_action="Record complete.",
                )
                return outcome
            except Exception as e:
                err_text = f"Gmail API error during send: {str(e)}"
                return f"FAILURE: Could not deliver via Gmail API: {err_text}"

        # Otherwise: Dry-Run simulation (either chosen by user or credentials.json not present)
        mode_note = "DRY-RUN SIMULATION (Approved locally)" if decision in ("APPROVED", "EDITED") else "DRY-RUN REQUESTED BY USER"
        save_draft_path = f"reports/draft_{recipient_name.replace(' ', '_').lower()}.eml"
        with open(save_draft_path, "w", encoding="utf-8") as f:
            f.write(f"To: {recipient_email}\nSubject: {final_subject}\n\n{final_body}")

        global_ledger.record_cycle(
            iteration=global_ledger.iteration_count,
            agent="Intelligent Outreach Agent",
            phase="ACT",
            observation=f"{mode_note} for {recipient_email}. Saved draft to {save_draft_path}.",
            decision="Simulated safe dispatch without sending live packet.",
            tool_called="Gmail Outreach Dispatcher",
            tool_input={"recipient": recipient_email, "subject": final_subject, "mode": mode_note},
            tool_output_summary=f"Draft saved to {save_draft_path}",
            evaluation="Safe local verification complete.",
            next_action="Task finished for contact.",
        )

        return (
            f"RESULT: {mode_note}.\n"
            f"- Recipient: {recipient_name} <{recipient_email}>\n"
            f"- Subject: {final_subject}\n"
            f"- Citations: {citations_used}\n"
            f"- Draft persisted to: {save_draft_path}\n"
            f"(Note: To enable live sending, place your Google OAuth 'credentials.json' in the project root)."
        )
