from typing import List
from models.schemas import ActionProposal, PolicyCheckResult, RiskAssessmentResult, GovernanceDecisionResult

class DecisionEngine:
    def make_decision(self, proposal: ActionProposal, policy_checks: List[PolicyCheckResult], risk: RiskAssessmentResult) -> GovernanceDecisionResult:
        # Check for hard blocks
        blocking_checks = [p for p in policy_checks if p.status == "BLOCK"]
        approval_checks = [p for p in policy_checks if p.status == "REQUIRE_APPROVAL"]

        if blocking_checks:
            decision = "BLOCK"
            status = "BLOCKED"
            reasons = [p.message for p in blocking_checks]
            explanation = f"Action BLOCKED by TrustLayer policy: {'; '.join(reasons)}"
        elif approval_checks:
            decision = "REQUIRE_APPROVAL"
            status = "PENDING_APPROVAL"
            reasons = [p.message for p in approval_checks]
            explanation = f"Action held for HUMAN APPROVAL: {'; '.join(reasons)}"
        elif risk.level == "HIGH":
            decision = "REQUIRE_APPROVAL"
            status = "PENDING_APPROVAL"
            explanation = f"Action held for HUMAN APPROVAL due to HIGH risk score ({risk.score}/100)."
        else:
            decision = "ALLOW"
            status = "ALLOWED"
            explanation = f"Action ALLOWED by TrustLayer (Risk: {risk.level}, Score: {risk.score}/100)."

        return GovernanceDecisionResult(
            action_id=proposal.action_id,
            decision=decision,
            risk=risk,
            policy_checks=policy_checks,
            explanation=explanation,
            status=status
        )

decision_engine = DecisionEngine()
