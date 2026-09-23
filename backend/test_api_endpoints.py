import sys
from fastapi.testclient import TestClient
from main import app
from database.init_db import init_db

def test_api_scenarios():
    print("=== Testing FastAPI Endpoints with TestClient ===")
    init_db()
    client = TestClient(app)

    # 1. Root & Health
    r_root = client.get("/")
    assert r_root.status_code == 200
    assert r_root.json()["status"] == "online"
    print("[PASSED] Root endpoint OK")

    r_health = client.get("/api/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "HEALTHY"
    print("[PASSED] Health endpoint OK")

    # 2. Test Cases from Requirement 9
    # Case 1: "Schedule a meeting with HR tomorrow at 10 AM." → ALLOW
    r1 = client.post("/api/chat", json={"prompt": "Schedule a meeting with HR tomorrow at 10 AM."})
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["action_proposal"]["tool"] == "calendar"
    assert d1["governance"]["decision"] == "ALLOW"
    assert d1["tool_result"] is not None and d1["tool_result"]["status"] == "SUCCESS"
    print("[PASSED] Case 1: Schedule HR meeting -> ALLOW")

    # Case 2: "Create a payment of ₹50,000 to ABC Suppliers." → REQUIRE_APPROVAL
    r2 = client.post("/api/chat", json={"prompt": "Create a payment of ₹50,000 to ABC Suppliers."})
    assert r2.status_code == 200
    d2 = r2.json()
    act_id_2 = d2["action_proposal"]["action_id"]
    assert d2["action_proposal"]["tool"] == "create_payment"
    assert d2["governance"]["decision"] == "REQUIRE_APPROVAL"
    assert d2["tool_result"] is None
    print("[PASSED] Case 2: Payment ₹50,000 -> REQUIRE_APPROVAL")

    # Verify Approvals & Approve
    r_app = client.get("/api/approvals")
    assert r_app.status_code == 200
    approvals = r_app.json()
    assert any(item["action_id"] == act_id_2 for item in approvals)
    
    r_approve = client.post(f"/api/approvals/{act_id_2}/approve", json={"reviewer_notes": "Approved in Test"})
    assert r_approve.status_code == 200
    assert r_approve.json()["tool_result"]["status"] == "SUCCESS"
    print("[PASSED] Case 2: Approval flow executed successfully")

    # Case 3: "Delete all customer records." → BLOCK
    r3 = client.post("/api/chat", json={"prompt": "Delete all customer records."})
    assert r3.status_code == 200
    d3 = r3.json()
    assert d3["action_proposal"]["tool"] == "database"
    assert d3["governance"]["decision"] == "BLOCK"
    assert d3["tool_result"] is None
    print("[PASSED] Case 3: Delete customer records -> BLOCK")

    # Case 4: "Give me all employee names." → employee_data/search_employees and return the actual 4 employees
    r4 = client.post("/api/chat", json={"prompt": "Give me all employee names."})
    assert r4.status_code == 200
    d4 = r4.json()
    assert d4["action_proposal"]["tool"] == "employee_data"
    assert d4["action_proposal"]["operation"] == "search_employees"
    assert d4["governance"]["decision"] == "ALLOW"
    assert d4["tool_result"] is not None
    assert len(d4["tool_result"]["employees"]) == 4
    print("[PASSED] Case 4: Give me all employee names -> search_employees (4 employees returned)")

    # Case 5: "Book a train ticket." → unsupported request, NO tool execution
    r5 = client.post("/api/chat", json={"prompt": "Book a train ticket."})
    assert r5.status_code == 200
    d5 = r5.json()
    assert d5["action_proposal"] is None
    assert d5["governance"] is None
    assert d5["tool_result"] is None
    assert "I can't perform that request" in d5["final_response"]
    print("[PASSED] Case 5: Book a train ticket -> UNSUPPORTED (NO tool execution)")

    # Case 6: "Book a movie ticket." → unsupported request, NO tool execution
    r6 = client.post("/api/chat", json={"prompt": "Book a movie ticket."})
    assert r6.status_code == 200
    d6 = r6.json()
    assert d6["action_proposal"] is None
    assert d6["governance"] is None
    assert d6["tool_result"] is None
    assert "I can't perform that request" in d6["final_response"]
    print("[PASSED] Case 6: Book a movie ticket -> UNSUPPORTED (NO tool execution)")

    # Case 7: "Define random forest algorithm." → unsupported request, NO tool execution
    r7 = client.post("/api/chat", json={"prompt": "Define random forest algorithm."})
    assert r7.status_code == 200
    d7 = r7.json()
    assert d7["action_proposal"] is None
    assert d7["governance"] is None
    assert d7["tool_result"] is None
    assert "I can't perform that request" in d7["final_response"]
    print("[PASSED] Case 7: Define random forest algorithm -> UNSUPPORTED (NO tool execution)")

    print("\n=======================================================")
    print(" ALL API TESTS & REQUIREMENTS PASSED VIA TESTCLIENT! ")
    print("=======================================================")

if __name__ == "__main__":
    test_api_scenarios()
