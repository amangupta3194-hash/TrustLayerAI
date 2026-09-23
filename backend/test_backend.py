import sys
import json
from database.init_db import init_db
from database.db import SessionLocal
from agent.llm_agent import ai_agent_service
from api.routes import approve_action, reject_action, get_pending_approvals

def test_pipeline():
    print("=== Testing TrustLayer AI Backend Pipeline ===")
    init_db()
    db = SessionLocal()
    try:
        # Scenario 1: Low Risk (Schedule HR Meeting)
        print("\n--- Testing Scenario 1: Low Risk (Meeting) ---")
        resp1 = ai_agent_service.process_user_request("Schedule a meeting with HR tomorrow at 10 AM.", "SES-001", db)
        print(f"Tool: {resp1.action_proposal.tool}")
        print(f"Decision: {resp1.governance.decision}")
        print(f"Risk Score: {resp1.governance.risk.score} ({resp1.governance.risk.level})")
        assert resp1.governance.decision == "ALLOW", f"Expected ALLOW, got {resp1.governance.decision}"
        assert resp1.tool_result is not None, "Tool should have executed for ALLOW decision"
        print("[PASSED] Scenario 1 PASSED!")

        # Scenario 2: High Risk Payment (Require Approval)
        print("\n--- Testing Scenario 2: High Risk Payment (Require Approval) ---")
        resp2 = ai_agent_service.process_user_request("Create a payment of INR 50,000 to ABC Suppliers.", "SES-002", db)
        print(f"Tool: {resp2.action_proposal.tool}")
        print(f"Decision: {resp2.governance.decision}")
        print(f"Risk Score: {resp2.governance.risk.score} ({resp2.governance.risk.level})")
        assert resp2.governance.decision == "REQUIRE_APPROVAL", f"Expected REQUIRE_APPROVAL, got {resp2.governance.decision}"
        assert resp2.tool_result is None, "Tool MUST NOT execute when approval is required"
        payment_act_id = resp2.action_proposal.action_id
        print("[PASSED] Scenario 2 PASSED!")

        # Scenario 3: Prohibited Action (Blocked)
        print("\n--- Testing Scenario 3: Prohibited Action (Blocked) ---")
        resp3 = ai_agent_service.process_user_request("Delete all customer records.", "SES-003", db)
        print(f"Tool: {resp3.action_proposal.tool}")
        print(f"Decision: {resp3.governance.decision}")
        print(f"Risk Score: {resp3.governance.risk.score} ({resp3.governance.risk.level})")
        assert resp3.governance.decision == "BLOCK", f"Expected BLOCK, got {resp3.governance.decision}"
        assert resp3.tool_result is None, "Tool MUST NOT execute when action is BLOCKED"
        print("[PASSED] Scenario 3 PASSED!")

        # Testing Approval Execution Flow
        print(f"\n--- Testing Approval Flow for Action {payment_act_id} ---")
        pending = get_pending_approvals(db)
        print(f"Pending Approvals Count: {len(pending)}")
        assert any(item["action_id"] == payment_act_id for item in pending), "Payment action should be in pending approvals list"

        approve_res = approve_action(payment_act_id, None, db)
        print(f"Approval Result: {approve_res['status']}")
        print(f"Executed Tool Output: {approve_res['tool_result']}")
        assert approve_res["status"] == "APPROVED", "Action should be approved"
        assert approve_res["tool_result"]["status"] == "SUCCESS", "Payment tool should execute upon approval"
        print("[PASSED] Approval Flow PASSED!")

        print("\nALL BACKEND PIPELINE VERIFICATION TESTS PASSED SUCCESSFULLY!")

    finally:
        db.close()

if __name__ == "__main__":
    test_pipeline()
