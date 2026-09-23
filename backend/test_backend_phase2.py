import json
from database.init_db import init_db
from database.db import SessionLocal
from api.routes import (
    get_health,
    get_dashboard_stats,
    get_risk_distribution,
    get_decision_distribution,
    get_action_detail,
    get_actions
)

def test_phase2_backend():
    print("=== Testing Phase 2 Backend Dashboard & Detail Endpoints ===")
    init_db()
    db = SessionLocal()
    try:
        # 1. Test System Health
        health = get_health(db)
        print("System Health Check:", health['status'], health['components'])
        assert health['status'] == "HEALTHY"
        assert health['components']['database'] == "CONNECTED"
        print("[PASSED] Health Endpoint Passed!")

        # 2. Test Dashboard Stats
        stats = get_dashboard_stats(db)
        print("Dashboard Stats:", stats)
        assert "total_actions" in stats
        assert "allowed_count" in stats
        assert "pending_approval_count" in stats
        assert "blocked_count" in stats
        assert "average_risk_score" in stats
        print("[PASSED] Dashboard Stats Endpoint Passed!")

        # 3. Test Risk Distribution
        risk_dist = get_risk_distribution(db)
        print("Risk Distribution:", risk_dist)
        assert "low_risk" in risk_dist
        assert "medium_risk" in risk_dist
        assert "high_risk" in risk_dist
        print("[PASSED] Risk Distribution Endpoint Passed!")

        # 4. Test Decision Distribution
        dec_dist = get_decision_distribution(db)
        print("Decision Distribution:", dec_dist)
        assert "ALLOW" in dec_dist
        assert "REQUIRE_APPROVAL" in dec_dist
        assert "BLOCK" in dec_dist
        print("[PASSED] Decision Distribution Endpoint Passed!")

        # 5. Test Action Details & Timeline
        actions = get_actions(limit=1, db=db)
        if actions:
            act_id = actions[0]["action_id"]
            detail = get_action_detail(act_id, db)
            print(f"Action Detail Timeline for '{act_id}': Steps count = {len(detail['timeline'])}")
            assert len(detail["timeline"]) >= 4
            print("[PASSED] Action Detail Timeline Endpoint Passed!")

        print("\nALL PHASE 2 BACKEND ENDPOINTS PASSED SUCCESSFULLY!")
    finally:
        db.close()

if __name__ == "__main__":
    test_phase2_backend()
