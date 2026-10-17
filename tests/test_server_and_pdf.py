import os
import pytest
from fastapi.testclient import TestClient
from server import app


def test_server_index_serving():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "Intelligence Crew" in response.text
    assert "webgl-canvas" in response.text


def test_research_api_generates_pdf_and_citations():
    client = TestClient(app)
    payload = {
        "query": "Autonomous agentic AI benchmarks 2026",
        "email": "test@enterprise.com",
    }
    response = client.post("/api/research", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "evidence" in data
    assert len(data["evidence"]) > 0
    assert "statistical_data" in data
    assert len(data["statistical_data"]) > 0
    assert "verification" in data
    assert data["verification"]["grounding_score"] == 100.0
    assert "pdf_filename" in data
    assert "pdf_download_url" in data
    assert data["pdf_filename"].endswith(".pdf")

    # Verify that the generated PDF actually exists on disk
    pdf_path = os.path.join("reports", data["pdf_filename"])
    assert os.path.exists(pdf_path)

    # Test download endpoint
    dl_response = client.get(data["pdf_download_url"])
    assert dl_response.status_code == 200
    assert dl_response.headers["content-type"] == "application/pdf"


def test_send_email_hitl_endpoint():
    client = TestClient(app)

    # Rejection test
    reject_res = client.post("/api/send-email", json={
        "recipient_email": "cto@company.com",
        "subject": "Test Subj",
        "body": "Test Body",
        "pdf_filename": "dummy.pdf",
        "decision": "REJECTED",
    })
    assert reject_res.status_code == 200
    assert reject_res.json()["status"] == "REJECTED"

    # Approval test (Dry run fallback without Gmail credentials)
    approve_res = client.post("/api/send-email", json={
        "recipient_email": "cto@company.com",
        "subject": "Test Subj",
        "body": "Test Body",
        "pdf_filename": "dummy.pdf",
        "decision": "APPROVED",
    })
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] in ("DRY_RUN_SAVED", "SENT")
