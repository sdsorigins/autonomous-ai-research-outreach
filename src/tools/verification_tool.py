import re
from typing import Type, List, Dict
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from src.memory import global_ledger


class VerificationInput(BaseModel):
    recipient_email: str = Field(description="Email address of the recipient being pitched")
    email_draft: str = Field(description="The full drafted email body and subject to audit")
    claims_to_check: List[str] = Field(
        description="List of specific factual claims asserted in the email draft"
    )


class ClaimVerifierTool(BaseTool):
    name: str = "Claim & Hallucination Verifier"
    description: str = (
        "Audits an outreach email draft against the verified Evidence Ledger. "
        "Verifies every factual statement against registered citations [E1], [E2], etc. "
        "Flags any hallucinated or unsupported claims and calculates an evidence grounding score."
    )
    args_schema: Type[BaseModel] = VerificationInput

    def _run(
        self,
        recipient_email: str,
        email_draft: str,
        claims_to_check: List[str],
    ) -> str:
        all_evidence = global_ledger.get_all_evidence()
        if not all_evidence:
            return (
                "AUDIT WARNING: Evidence Ledger is currently empty! "
                "Cannot ground any claims. Flagging all claims as UNSUPPORTED."
            )

        # Build combined evidence text for lexical/semantic grounding matching
        combined_evidence = " ".join([f"{e.fact} {e.snippet}" for e in all_evidence]).lower()

        verified_claims = []
        unsupported_claims = []

        for claim in claims_to_check:
            claim_words = [w.lower() for w in re.findall(r"\b[A-Za-z0-9\$\%]{3,}\b", claim)]
            matched_evidence_ids = []

            for ev in all_evidence:
                ev_text = f"{ev.fact} {ev.snippet}".lower()
                # Check for significant token overlaps or key entities
                overlap = sum(1 for w in claim_words if w in ev_text)
                match_ratio = overlap / max(len(claim_words), 1)

                if match_ratio >= 0.4 or any(
                    part.lower() in ev_text for part in claim.split(",") if len(part.strip()) > 8
                ):
                    matched_evidence_ids.append(ev.id)

            if matched_evidence_ids:
                verified_claims.append({
                    "claim": claim,
                    "citations": list(set(matched_evidence_ids)),
                })
            else:
                unsupported_claims.append(claim)

        total_claims = len(claims_to_check)
        grounding_score = (len(verified_claims) / max(total_claims, 1)) * 100.0
        status = "PASSED" if not unsupported_claims else "FLAGGED"

        # Record audit trail
        global_ledger.record_cycle(
            iteration=global_ledger.iteration_count,
            agent="Intelligent Outreach Agent",
            phase="EVALUATE",
            observation=f"Audited draft for {recipient_email}. Grounding score: {grounding_score:.1f}%",
            decision=f"Status {status}. {len(unsupported_claims)} unsupported claims flagged.",
            tool_called="Claim & Hallucination Verifier",
            tool_input={"recipient": recipient_email, "claims_count": total_claims},
            tool_output_summary=f"Verified: {len(verified_claims)}, Unsupported: {len(unsupported_claims)}",
            evaluation=f"Status: {status}, Grounding: {grounding_score:.1f}%",
            next_action="Request revision or prompt user approval" if status == "PASSED" else "Remove unsupported assertions",
        )

        report = [
            f"=== CLAIM VERIFICATION AUDIT FOR: {recipient_email} ===",
            f"Grounding Score: {grounding_score:.1f}% ({len(verified_claims)}/{total_claims} verified)",
            f"Audit Status: {status}\n",
        ]

        if verified_claims:
            report.append("VERIFIED CLAIMS:")
            for vc in verified_claims:
                citations_str = ", ".join(vc["citations"])
                report.append(f"  [PASS] \"{vc['claim']}\" -> Anchored in {citations_str}")

        if unsupported_claims:
            report.append("\nUNSUPPORTED CLAIMS (FLAGGED):")
            for uc in unsupported_claims:
                report.append(f"  [FLAGGED] \"{uc}\" -> No verified evidence found in ledger!")
            report.append("\nACTION REQUIRED: Remove or adjust the flagged statements before finalizing.")
        else:
            report.append("\nNO HALLUCINATIONS DETECTED: All factual statements are supported by evidence citations.")

        return "\n".join(report)


class ResearchRequestInput(BaseModel):
    contact_name: str = Field(description="Name of the contact who needs more research")
    missing_information: str = Field(description="Specific critical information missing")
    recommended_query: str = Field(description="Search query recommended for Agent 1 to run")


class RequestMoreResearchTool(BaseTool):
    name: str = "Request Additional Research"
    description: str = (
        "Invoked by the Outreach Agent when critical information about a contact or topic is missing. "
        "Sends a targeted research request back to the Autonomous Research Agent (Agent 1) to initiate "
        "an adaptive feedback loop and retrieve missing evidence."
    )
    args_schema: Type[BaseModel] = ResearchRequestInput

    def _run(
        self,
        contact_name: str,
        missing_information: str,
        recommended_query: str,
    ) -> str:
        global_ledger.feedback_loops_count += 1

        # Record feedback loop in audit ledger
        global_ledger.record_cycle(
            iteration=global_ledger.iteration_count,
            agent="Intelligent Outreach Agent",
            phase="LOOPBACK",
            observation=f"Missing vital info for {contact_name}: {missing_information}",
            decision=f"Trigger feedback loop back to Agent 1 with query: '{recommended_query}'",
            tool_called="Request Additional Research",
            tool_input={
                "contact": contact_name,
                "missing_information": missing_information,
                "recommended_query": recommended_query,
            },
            tool_output_summary="Feedback loop dispatched to Research Agent",
            evaluation="Re-opening research phase for targeted query",
            next_action="Agent 1 executes adaptive web search",
        )

        return (
            f"FEEDBACK LOOP INITIATED:\n"
            f"Dispatched targeted research request to Agent 1 for {contact_name}.\n"
            f"Target Query: '{recommended_query}'\n"
            f"Missing Fact: {missing_information}\n"
            f"Orchestrator will route this request to execute research and refresh Evidence Ledger."
        )
