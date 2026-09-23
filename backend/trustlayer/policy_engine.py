from typing import List, Dict, Any
from models.schemas import ActionProposal, PolicyCheckResult
from tools.registry import tool_registry

class PolicyEngine:
    def evaluate(self, proposal: ActionProposal) -> List[PolicyCheckResult]:
        checks: List[PolicyCheckResult] = []
        params = proposal.parameters or {}
        tool_name = proposal.tool
        op = proposal.operation.lower()

        # P-006: Agent Tool Permission Check
        valid_tools = [t["name"] for t in tool_registry.get_tools_schema()]
        if tool_name not in valid_tools:
            checks.append(PolicyCheckResult(
                policy_id="P-006",
                policy_name="Agent Tool Permission",
                status="BLOCK",
                severity="HIGH",
                message=f"Agent attempt to call unauthorized tool '{tool_name}'."
            ))

        # P-001: Payment Threshold Check
        if tool_name == "create_payment":
            amount = float(params.get("amount", 0))
            if amount > 10000:
                checks.append(PolicyCheckResult(
                    policy_id="P-001",
                    policy_name="Payment Threshold",
                    status="REQUIRE_APPROVAL",
                    severity="HIGH",
                    message=f"Payment amount of ₹{amount:,.2f} exceeds threshold limit of ₹10,000."
                ))
            else:
                checks.append(PolicyCheckResult(
                    policy_id="P-001",
                    policy_name="Payment Threshold",
                    status="PASS",
                    severity="LOW",
                    message="Payment amount is within safe automated threshold."
                ))

        # P-002: Confidential External Data Export Check
        if tool_name == "send_email":
            recipient = str(params.get("recipient", "")).lower()
            body = str(params.get("body", "")).lower()
            # If body contains sensitive employee keyword and recipient is external
            is_external = not (recipient.endswith("@company.com") or recipient.endswith("@internal.org"))
            has_sensitive = any(kw in body for kw in ["salary", "ssn", "confidential", "employee record", "payroll"])
            if is_external and has_sensitive:
                checks.append(PolicyCheckResult(
                    policy_id="P-002",
                    policy_name="Confidential External Data",
                    status="BLOCK",
                    severity="CRITICAL",
                    message=f"Sending confidential employee data to external address '{recipient}' is prohibited."
                ))

        # P-003: Destructive Database Operation Check
        if tool_name == "database" and op == "delete_record":
            scope = str(params.get("scope", "")).lower()
            target = str(params.get("target", "")).lower()
            is_bulk = params.get("all_records") is True or scope in ["all", "bulk"] or "all" in target
            if is_bulk:
                checks.append(PolicyCheckResult(
                    policy_id="P-003",
                    policy_name="Destructive Database Operation",
                    status="BLOCK",
                    severity="CRITICAL",
                    message="Bulk deletion of customer records is strictly prohibited by policy P-003."
                ))

        # P-004: Sensitive Employee Data Authorization Check
        if tool_name == "employee_data":
            query = str(params.get("query", "")).lower()
            fields = str(params.get("fields", "")).lower()
            if "salary" in query or "salary" in fields or params.get("include_salary") is True:
                checks.append(PolicyCheckResult(
                    policy_id="P-004",
                    policy_name="Sensitive Employee Data",
                    status="REQUIRE_APPROVAL",
                    severity="MEDIUM",
                    message="Accessing employee salary information requires elevated human authorization."
                ))

        # P-005: Bulk Operations Check
        record_count = int(params.get("affected_count", params.get("count", 0)))
        if record_count > 100:
            checks.append(PolicyCheckResult(
                policy_id="P-005",
                policy_name="Bulk Operations",
                status="REQUIRE_APPROVAL",
                severity="MEDIUM",
                message=f"Operation affects {record_count} records (> 100 limit), requiring human review."
            ))

        return checks

policy_engine = PolicyEngine()
