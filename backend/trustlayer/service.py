import json
from datetime import datetime
from sqlalchemy.orm import Session
from models.schemas import ActionProposal, GovernanceDecisionResult
from trustlayer.action_monitor import action_monitor
from trustlayer.policy_engine import policy_engine
from trustlayer.risk_engine import risk_engine
from trustlayer.decision_engine import decision_engine
from database.models import ActionProposalDB, RiskAssessmentDB, ApprovalDB, AuditLogDB

class TrustLayerService:
    def evaluate_and_record(self, proposal: ActionProposal, user_prompt: str, db: Session) -> GovernanceDecisionResult:
        # 1. Action Monitoring
        monitored_data = action_monitor.capture_action(proposal)

        # 2. Policy Engine Evaluation
        policy_results = policy_engine.evaluate(proposal)

        # 3. Risk Engine Calculation
        risk_result = risk_engine.calculate_risk(proposal, policy_results)

        # 4. Decision Engine Synthesis
        governance_decision = decision_engine.make_decision(proposal, policy_results, risk_result)

        now_iso = datetime.utcnow().isoformat() + "Z"

        # 5. DB Persistence
        action_db = ActionProposalDB(
            action_id=proposal.action_id,
            agent_id=proposal.agent_id,
            session_id=proposal.session_id,
            tool=proposal.tool,
            operation=proposal.operation,
            parameters_json=json.dumps(proposal.parameters),
            requested_at=proposal.requested_at,
            status=governance_decision.status,
            risk_score=risk_result.score,
            risk_level=risk_result.level,
            decision=governance_decision.decision,
            reason=governance_decision.explanation,
            user_prompt=user_prompt
        )
        db.add(action_db)

        risk_db = RiskAssessmentDB(
            action_id=proposal.action_id,
            score=risk_result.score,
            level=risk_result.level,
            factors_json=json.dumps(risk_result.factors),
            explanation=risk_result.explanation,
            created_at=now_iso
        )
        db.add(risk_db)

        # Create audit entry for proposal & decision
        audit_1 = AuditLogDB(
            action_id=proposal.action_id,
            event_type="ACTION_PROPOSED",
            actor="AI_AGENT",
            details_json=json.dumps({"tool": proposal.tool, "operation": proposal.operation, "parameters": proposal.parameters}),
            timestamp=now_iso
        )
        audit_2 = AuditLogDB(
            action_id=proposal.action_id,
            event_type="DECISION_MADE",
            actor="TRUSTLAYER",
            details_json=json.dumps({
                "decision": governance_decision.decision,
                "status": governance_decision.status,
                "risk_score": risk_result.score,
                "risk_level": risk_result.level,
                "explanation": governance_decision.explanation
            }),
            timestamp=now_iso
        )
        db.add(audit_1)
        db.add(audit_2)

        # If REQUIRE_APPROVAL, create pending approval record
        if governance_decision.decision == "REQUIRE_APPROVAL":
            approval_db = ApprovalDB(
                action_id=proposal.action_id,
                status="PENDING",
                requested_at=now_iso
            )
            db.add(approval_db)

            audit_3 = AuditLogDB(
                action_id=proposal.action_id,
                event_type="APPROVAL_REQUESTED",
                actor="TRUSTLAYER",
                details_json=json.dumps({"reason": governance_decision.explanation}),
                timestamp=now_iso
            )
            db.add(audit_3)

        db.commit()

        return governance_decision

trustlayer_service = TrustLayerService()
