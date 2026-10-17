import os
import pytest
from unittest.mock import patch
from src.tools.gmail_tool import GmailOutreachTool, GmailServiceWrapper, GmailApprovalManager


def test_gmail_message_payload_creation():
    payload = GmailServiceWrapper.create_message(
        to="test.user@example.com",
        subject="Agentic AI Inquiry",
        body="This is an evidence-grounded outreach email.",
    )
    assert "raw" in payload
    assert isinstance(payload["raw"], str)
    assert len(payload["raw"]) > 10


def test_gmail_user_rejection_halts_transmission():
    tool = GmailOutreachTool()

    # Mock user input choosing 'R' (Reject)
    with patch.object(GmailApprovalManager, "prompt_user_for_approval", return_value=("REJECTED", "Subj", "Body")):
        result = tool._run(
            recipient_name="John Doe",
            recipient_email="john@example.com",
            subject="Subj",
            body="Body",
        )

        assert "REJECTED" in result
        assert "No message was sent" in result


def test_gmail_dry_run_saves_local_eml():
    tool = GmailOutreachTool()
    os.makedirs("reports", exist_ok=True)

    with patch.object(GmailApprovalManager, "prompt_user_for_approval", return_value=("DRY_RUN", "Dry Subject", "Dry Body")):
        result = tool._run(
            recipient_name="Alice Smith",
            recipient_email="alice@example.com",
            subject="Dry Subject",
            body="Dry Body",
            citations_used="[E1]",
        )

        assert "DRY-RUN" in result
        expected_file = "reports/draft_alice_smith.eml"
        assert os.path.exists(expected_file)
        with open(expected_file, "r", encoding="utf-8") as f:
            content = f.read()
            assert "Dry Subject" in content
            assert "Dry Body" in content
