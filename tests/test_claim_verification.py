import pytest
from src.memory import global_ledger
from src.tools.verification_tool import ClaimVerifierTool, RequestMoreResearchTool


def test_claim_verification_grounding():
    global_ledger.reset()

    # Prepopulate evidence ledger
    global_ledger.add_evidence(
        fact="Acme AI reduced customer support resolution time by 52%",
        source_title="Acme Case Study",
        source_url="https://acme.example.com/case-study",
        snippet="Customer support resolution time dropped by 52% after deploying autonomous agents.",
        query_used="Acme AI support resolution benchmark",
        confidence=0.95,
    )

    verifier = ClaimVerifierTool()

    # Case 1: Grounded claim
    grounded_report = verifier._run(
        recipient_email="cto@enterprise.com",
        email_draft="Acme AI reduced customer support resolution time by 52% in enterprise trials.",
        claims_to_check=["Acme AI reduced customer support resolution time by 52%"],
    )
    assert "Audit Status: PASSED" in grounded_report
    assert "Grounding Score: 100.0%" in grounded_report
    assert "[PASS]" in grounded_report
    assert "[E1]" in grounded_report

    # Case 2: Hallucinated / Unsupported claim
    unsupported_report = verifier._run(
        recipient_email="cto@enterprise.com",
        email_draft="We are partnering with NASA on deep space missions.",
        claims_to_check=["We are partnering with NASA on deep space missions"],
    )
    assert "Audit Status: FLAGGED" in unsupported_report
    assert "UNSUPPORTED CLAIMS (FLAGGED)" in unsupported_report
    assert "[FLAGGED]" in unsupported_report


def test_request_more_research_feedback_loop():
    global_ledger.reset()
    assert global_ledger.feedback_loops_count == 0

    tool = RequestMoreResearchTool()
    response = tool._run(
        contact_name="Marcus Vance",
        missing_information="SOC2 Type II compliance verification",
        recommended_query="Acme AI SOC2 Type II compliance audit report",
    )

    assert "FEEDBACK LOOP INITIATED" in response
    assert global_ledger.feedback_loops_count == 1
    assert any(r.phase == "LOOPBACK" for r in global_ledger.audit_records)
