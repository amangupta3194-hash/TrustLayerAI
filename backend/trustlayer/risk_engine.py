from typing import List, Dict, Any
from models.schemas import ActionProposal, PolicyCheckResult, RiskAssessmentResult

class RiskEngine:
    def calculate_risk(self, proposal: ActionProposal, policy_checks: List[PolicyCheckResult]) -> RiskAssessmentResult:
        tool = proposal.tool
        op = proposal.operation.lower()
        params = proposal.parameters or {}

        # Default scores
        data_sensitivity = 5
        system_impact = 5
        financial_impact = 0
        security_risk = 5
        policy_risk = 0
        authorization_risk = 5

        # 1. Financial Impact
        if tool == "create_payment":
            amount = float(params.get("amount", 0))
            if amount <= 1000:
                financial_impact = 10
            elif amount <= 10000:
                financial_impact = 15
            else:
                financial_impact = 20

        # 2. System Impact & Security Risk
        if tool == "database":
            if op == "delete_record":
                scope = str(params.get("scope", "")).lower()
                target = str(params.get("target", "")).lower()
                is_bulk = params.get("all_records") is True or scope in ["all", "bulk"] or "all" in target
                if is_bulk:
                    system_impact = 20
                    security_risk = 20
                    data_sensitivity = 18
                else:
                    system_impact = 12
                    security_risk = 10
            elif op == "update_record":
                system_impact = 10
            elif op == "read_record":
                system_impact = 2

        # 3. Data Sensitivity
        if tool == "employee_data":
            query = str(params.get("query", "")).lower()
            if "salary" in query or params.get("include_salary") is True:
                data_sensitivity = 18
                authorization_risk = 9
            else:
                data_sensitivity = 10

        if tool == "send_email":
            recipient = str(params.get("recipient", "")).lower()
            if not (recipient.endswith("@company.com") or recipient.endswith("@internal.org")):
                security_risk = 16
                authorization_risk = 8

        if tool == "calendar":
            data_sensitivity = 4
            system_impact = 3
            financial_impact = 0
            security_risk = 3
            authorization_risk = 2

        # 4. Policy Risk Factor based on checks
        for p in policy_checks:
            if p.status == "BLOCK":
                policy_risk = max(policy_risk, 10)
                security_risk = max(security_risk, 18)
            elif p.status == "REQUIRE_APPROVAL":
                policy_risk = max(policy_risk, 8)

        total_score = min(100, data_sensitivity + system_impact + financial_impact + security_risk + policy_risk + authorization_risk)

        if total_score <= 30:
            level = "LOW"
        elif total_score <= 70:
            level = "MEDIUM"
        else:
            level = "HIGH"

        explanation_parts = []
        if financial_impact > 10:
            explanation_parts.append(f"Financial exposure is high ({financial_impact}/20)")
        if system_impact > 10:
            explanation_parts.append(f"System impact level is elevated ({system_impact}/20)")
        if security_risk > 10:
            explanation_parts.append(f"Security risk score is high ({security_risk}/20)")
        if data_sensitivity > 10:
            explanation_parts.append(f"Data sensitivity is elevated ({data_sensitivity}/20)")
        if policy_risk > 0:
            explanation_parts.append(f"Policy risk detected ({policy_risk}/10)")

        if not explanation_parts:
            explanation_parts.append("Low risk operation within standard security baselines")

        return RiskAssessmentResult(
            score=total_score,
            level=level,
            factors={
                "data_sensitivity": data_sensitivity,
                "system_impact": system_impact,
                "financial_impact": financial_impact,
                "security_risk": security_risk,
                "policy_risk": policy_risk,
                "authorization_risk": authorization_risk
            },
            explanation="; ".join(explanation_parts) + "."
        )

risk_engine = RiskEngine()
