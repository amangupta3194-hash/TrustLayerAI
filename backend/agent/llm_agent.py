import os
import json
import uuid
import httpx
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session

from models.schemas import ActionProposal, ChatResponse
from trustlayer.service import trustlayer_service
from tools.registry import tool_registry
from database.models import ActionProposalDB, AuditLogDB

class AIAgentService:
    def __init__(self):
        self.agent_id = "trustops-agent"

    def process_user_request(self, user_prompt: str, session_id: str, db: Session) -> ChatResponse:
        sess_id = session_id or f"SES-{uuid.uuid4().hex[:6].upper()}"
        act_id = f"ACT-{uuid.uuid4().hex[:6].upper()}"
        now_iso = datetime.utcnow().isoformat() + "Z"

        # 1. Determine structured action proposal (LLM or deterministic fallback)
        proposal = self._generate_action_proposal(user_prompt, act_id, sess_id, now_iso)

        # 2. Reject unsupported / unrelated requests or invalid operations without tool execution or policy violation
        if not proposal or not tool_registry.is_valid_operation(proposal.tool, proposal.operation):
            return ChatResponse(
                user_prompt=user_prompt,
                action_proposal=None,
                governance=None,
                tool_result=None,
                final_response=(
                    "I can't perform that request. TrustOps AI currently supports governed enterprise "
                    "actions such as calendar, payments, database operations, employee data, and email."
                )
            )

        # 3. MUST route valid proposal ONLY through TrustLayer
        governance_res = trustlayer_service.evaluate_and_record(proposal, user_prompt, db)

        tool_result = None
        final_response = ""

        # 4. Handle governance decision & formulate natural final response
        if governance_res.decision == "ALLOW":
            # Execute tool through authorized TrustLayer path ONLY
            tool_result = tool_registry.execute_tool(
                tool_name=proposal.tool,
                operation=proposal.operation,
                parameters=proposal.parameters
            )
            
            # Record execution in DB and audit
            act_db = db.query(ActionProposalDB).filter(ActionProposalDB.action_id == proposal.action_id).first()
            if act_db:
                act_db.status = "EXECUTED"
                act_db.execution_result_json = json.dumps(tool_result)
                
            audit = AuditLogDB(
                action_id=proposal.action_id,
                event_type="TOOL_EXECUTED",
                actor="TRUSTLAYER_GATEWAY",
                details_json=json.dumps(tool_result),
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
            db.add(audit)
            db.commit()

            # Dynamic natural response based on real tool output
            final_response = self._build_natural_success_response(proposal, tool_result)

        elif governance_res.decision == "REQUIRE_APPROVAL":
            amount_str = ""
            if "amount" in proposal.parameters:
                amt = proposal.parameters.get("amount", 0)
                curr = proposal.parameters.get("currency", "INR")
                amount_str = f"\n\n**Amount**: {curr} {amt:,.2f}"

            final_response = (
                f"This action requires human approval before it can be executed.{amount_str}\n\n"
                f"**Risk**: {governance_res.risk.score} / 100 — {governance_res.risk.level}\n"
                f"**Status**: Waiting for administrator authorization in the Approvals Queue."
            )

        elif governance_res.decision == "BLOCK":
            act_db = db.query(ActionProposalDB).filter(ActionProposalDB.action_id == proposal.action_id).first()
            if act_db:
                act_db.status = "BLOCKED"
                
            audit = AuditLogDB(
                action_id=proposal.action_id,
                event_type="ACTION_BLOCKED",
                actor="TRUSTLAYER",
                details_json=json.dumps({"reason": governance_res.explanation}),
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
            db.add(audit)
            db.commit()

            policy_id_str = "P-003 — Security Policy"
            if governance_res.policy_checks:
                policy_id_str = f"{governance_res.policy_checks[0].policy_id} — {governance_res.policy_checks[0].policy_name}"

            final_response = (
                f"I can't complete this request because it is blocked by the organization's security policy.\n\n"
                f"**Blocked by**: {policy_id_str}\n"
                f"**Risk**: {governance_res.risk.score} / 100 — {governance_res.risk.level}\n"
                f"**Reason**: {governance_res.explanation}"
            )

        return ChatResponse(
            user_prompt=user_prompt,
            action_proposal=proposal,
            governance=governance_res,
            tool_result=tool_result,
            final_response=final_response
        )

    def _build_natural_success_response(self, proposal: ActionProposal, tool_result: Dict[str, Any]) -> str:
        tool = proposal.tool
        params = proposal.parameters or {}

        if tool == "create_payment":
            vendor = params.get("vendor", "Vendor")
            amount = params.get("amount", 0)
            currency = params.get("currency", "INR")
            txn_id = tool_result.get("transaction_id", "TXN-SUCCESS")
            return f"Payment of {currency} {amount:,.2f} to {vendor} was successfully created.\n\n**Transaction ID**: `{txn_id}`"

        elif tool == "calendar":
            title = params.get("title", "Meeting")
            time_val = params.get("time", "scheduled time")
            mtg_id = tool_result.get("meeting_id", "MTG-SUCCESS")
            return f"Your meeting '{title}' has been successfully scheduled for {time_val}.\n\n**Meeting ID**: `{mtg_id}`"

        elif tool == "send_email":
            recipient = params.get("recipient", "recipient")
            msg_id = tool_result.get("message_id", "MSG-SUCCESS")
            return f"Email was successfully sent to {recipient}.\n\n**Message ID**: `{msg_id}`"

        elif tool == "employee_data":
            status = tool_result.get("status")
            if status != "SUCCESS":
                err_msg = tool_result.get("message", "")
                if "Unsupported operation" in err_msg:
                    return "I can't perform that specific employee data operation. TrustOps AI supports searching employees, viewing details, managers, and reporting structure."
                return err_msg or "Unable to retrieve employee records."
            
            op = proposal.operation
            if op in ["search_employees", "list_employees"]:
                employees = tool_result.get("employees", [])
                if not employees:
                    return "No matching employee records found in the directory."
                names = [f"- **{emp['name']}** ({emp['role']} - {emp['department']})" for emp in employees]
                return f"Retrieved {len(employees)} employee record(s) from directory:\n" + "\n".join(names)

            elif op == "get_employee":
                emp = tool_result.get("employee")
                if not emp:
                    return "Employee details could not be found in the directory."
                return (
                    f"Here are the details for **{emp['name']}**:\n"
                    f"- **Employee ID**: {emp['employee_id']}\n"
                    f"- **Department**: {emp['department']}\n"
                    f"- **Role**: {emp['role']}\n"
                    f"- **Email**: {emp['email']}\n"
                    f"- **Salary**: {emp['salary']}"
                )

            elif op == "get_manager":
                emp = tool_result.get("employee")
                manager = tool_result.get("manager")
                if not manager:
                    emp_name = emp.get('name', 'Employee') if emp else 'The employee'
                    return f"**{emp_name}** does not have a manager assigned."
                return f"The manager of **{emp['name']}** is **{manager['name']}** ({manager['role']})."

            elif op == "list_managers":
                managers = tool_result.get("managers", [])
                if not managers:
                    return "No managers found in the directory."
                return "Here are all managers:\n" + "\n".join([f"- {m['name']} ({m['role']})" for m in managers])

            elif op == "get_reports":
                manager = tool_result.get("manager")
                mgr_name = manager.get('name', 'Manager') if manager else 'Manager'
                reports = tool_result.get("reports", [])
                if not reports:
                    return f"No employees report to **{mgr_name}**."
                names = [r["name"] for r in reports]
                return f"The following employees report to **{mgr_name}**:\n" + "\n".join([f"- {name}" for name in names])

            return "Employee directory query completed successfully."

        elif tool == "database":
            op = proposal.operation
            target = params.get("target", "database")
            return f"Database operation `{op}` on {target} completed successfully."

        return f"Action using tool `{tool}` completed successfully."

    def _generate_action_proposal(self, user_prompt: str, action_id: str, session_id: str, requested_at: str) -> Optional[ActionProposal]:
        api_key = os.getenv("LLM_API_KEY")
        provider = os.getenv("LLM_PROVIDER")

        if api_key and provider:
            try:
                proposal = self._call_llm_for_proposal(user_prompt, action_id, session_id, requested_at, provider, api_key)
                if proposal:
                    return proposal
            except Exception as e:
                print(f"LLM Provider error: {e}. Falling back to deterministic agent.")

        return self._deterministic_fallback_parser(user_prompt, action_id, session_id, requested_at)

    def _deterministic_fallback_parser(self, prompt: str, action_id: str, session_id: str, requested_at: str) -> Optional[ActionProposal]:
        p_lower = prompt.lower().strip()

        # Check for explicitly unrelated / non-enterprise keywords first
        unrelated_indicators = [
            "train ticket", "movie ticket", "flight ticket", "bus ticket", "hotel", 
            "book a ticket", "book ticket", "random forest", "algorithm",
            "weather", "pizza", "burger", "recipe", "joke", "translate"
        ]
        if any(indicator in p_lower for indicator in unrelated_indicators):
            # Unless it specifically contains database/payment/calendar/employee keywords:
            if not any(k in p_lower for k in ["meeting", "customer record", "employee", "salary", "supplier", "vendor"]):
                return None

        # Scenario 1: Calendar / Meeting
        if "meeting" in p_lower or "calendar" in p_lower or "schedule a meeting" in p_lower or "schedule meeting" in p_lower or "team sync" in p_lower or "standup" in p_lower:
            return ActionProposal(
                action_id=action_id,
                agent_id=self.agent_id,
                session_id=session_id,
                tool="calendar",
                operation="create_meeting",
                parameters={
                    "title": "HR Meeting" if "hr" in p_lower else "Team Sync",
                    "participant": "HR Team" if "hr" in p_lower else "Engineering",
                    "time": "Tomorrow at 10:00 AM" if "10" in p_lower else "Friday at 3 PM"
                },
                requested_at=requested_at
            )

        # Scenario 2: Payment
        elif "payment" in p_lower or "pay " in p_lower or "pay to" in p_lower or "transfer" in p_lower or "₹" in prompt or "$" in prompt:
            # Avoid non-financial uses
            if any(term in p_lower for term in ["payment", "pay", "transfer", "₹", "$", "inr", "usd", "supplier", "vendor"]):
                amount = 50000
                for word in p_lower.replace("₹", "").replace(",", "").replace("$", "").split():
                    if word.isdigit():
                        amount = int(word)
                        break
                vendor = "ABC Suppliers" if "abc" in p_lower else ("XYZ Traders" if "xyz" in p_lower else "External Vendor")
                return ActionProposal(
                    action_id=action_id,
                    agent_id=self.agent_id,
                    session_id=session_id,
                    tool="create_payment",
                    operation="create",
                    parameters={
                        "vendor": vendor,
                        "amount": amount,
                        "currency": "INR"
                    },
                    requested_at=requested_at
                )

        # Scenario 3: Database Deletion / Bulk Delete / Read / Update
        elif ("customer record" in p_lower or "customer records" in p_lower or "database" in p_lower or 
              ("delete" in p_lower and ("record" in p_lower or "customer" in p_lower or "table" in p_lower or "all" in p_lower)) or
              ("purge" in p_lower and "record" in p_lower) or
              ("drop" in p_lower and ("table" in p_lower or "database" in p_lower))):
            
            is_delete = any(w in p_lower for w in ["delete", "remove", "drop", "purge"])
            is_bulk = "all" in p_lower or "customer" in p_lower or "bulk" in p_lower or "entire" in p_lower
            
            if is_delete:
                return ActionProposal(
                    action_id=action_id,
                    agent_id=self.agent_id,
                    session_id=session_id,
                    tool="database",
                    operation="delete_record",
                    parameters={
                        "target": "customer_records",
                        "scope": "all" if is_bulk else "single",
                        "all_records": is_bulk,
                        "record_id": "CUST-001" if not is_bulk else None
                    },
                    requested_at=requested_at
                )
            elif "update" in p_lower or "modify" in p_lower:
                return ActionProposal(
                    action_id=action_id,
                    agent_id=self.agent_id,
                    session_id=session_id,
                    tool="database",
                    operation="update_record",
                    parameters={
                        "target": "customer_records",
                        "record_id": "CUST-001"
                    },
                    requested_at=requested_at
                )
            else:
                return ActionProposal(
                    action_id=action_id,
                    agent_id=self.agent_id,
                    session_id=session_id,
                    tool="database",
                    operation="read_record",
                    parameters={"target": "customer_records"},
                    requested_at=requested_at
                )

        # Employee Data / Salary / Manager queries
        elif "employee" in p_lower or "salary" in p_lower or "staff" in p_lower or "manager" in p_lower or ("report" in p_lower and not "bug" in p_lower) or any(name in p_lower for name in ["alice", "bob", "carol", "david"]):
            # Case 3: Who is the manager of Alice?
            if "manager of" in p_lower or ("who is" in p_lower and "manager" in p_lower) or ("who manages" in p_lower):
                target_name = None
                for name in ["alice", "bob", "carol", "david"]:
                    if name in p_lower:
                        target_name = name.title()
                        break
                return ActionProposal(
                    action_id=action_id,
                    agent_id=self.agent_id,
                    session_id=session_id,
                    tool="employee_data",
                    operation="get_manager",
                    parameters={
                        "employee_name": target_name or "Alice"
                    },
                    requested_at=requested_at
                )
            
            # Case 4: Show all managers
            elif "all managers" in p_lower or "show all managers" in p_lower or "list managers" in p_lower:
                return ActionProposal(
                    action_id=action_id,
                    agent_id=self.agent_id,
                    session_id=session_id,
                    tool="employee_data",
                    operation="list_managers",
                    parameters={},
                    requested_at=requested_at
                )
                
            # Case 5: Which employees report to David?
            elif "report" in p_lower:
                target_name = None
                for name in ["alice", "bob", "carol", "david"]:
                    if name in p_lower:
                        target_name = name.title()
                        break
                return ActionProposal(
                    action_id=action_id,
                    agent_id=self.agent_id,
                    session_id=session_id,
                    tool="employee_data",
                    operation="get_reports",
                    parameters={
                        "manager_name": target_name or "David"
                    },
                    requested_at=requested_at
                )

            # Case 2: Show Alice's details
            elif any(name in p_lower for name in ["alice", "bob", "carol", "david"]) and not "all" in p_lower and not "names" in p_lower:
                target_name = None
                for name in ["alice", "bob", "carol", "david"]:
                    if name in p_lower:
                        target_name = name.title()
                        break
                return ActionProposal(
                    action_id=action_id,
                    agent_id=self.agent_id,
                    session_id=session_id,
                    tool="employee_data",
                    operation="get_employee",
                    parameters={
                        "name": target_name
                    },
                    requested_at=requested_at
                )

            # Case 1: Give me all employee names / list employees
            else:
                return ActionProposal(
                    action_id=action_id,
                    agent_id=self.agent_id,
                    session_id=session_id,
                    tool="employee_data",
                    operation="search_employees",
                    parameters={},
                    requested_at=requested_at
                )

        # Email
        elif "email" in p_lower or "send an email" in p_lower or "send email" in p_lower or ("mail to" in p_lower and "@" in p_lower):
            return ActionProposal(
                action_id=action_id,
                agent_id=self.agent_id,
                session_id=session_id,
                tool="send_email",
                operation="send_email",
                parameters={
                    "recipient": "finance@company.com" if "finance" in p_lower else ("external.partner@vendor.org" if "external" in p_lower else "alice.smith@company.com"),
                    "subject": "System Notification",
                    "body": f"Automated response request for: {prompt}"
                },
                requested_at=requested_at
            )

        # If none of the enterprise tools matched, return None (unsupported request)
        return None

    def _call_llm_for_proposal(self, prompt: str, action_id: str, session_id: str, requested_at: str, provider: str, api_key: str) -> Optional[ActionProposal]:
        tools_schema = tool_registry.get_tools_schema()
        system_prompt = (
            "You are TrustOps AI agent. You convert enterprise user requests into structured action proposals for TrustLayer governance.\n\n"
            "REGISTERED ENTERPRISE TOOLS & OPERATIONS:\n"
            "- employee_data: Access employee directory and records.\n"
            "  - 'search_employees': List all employees or search directory (parameters: {} for all, or {'query': '...'})\n"
            "  - 'get_employee': Get specific employee details (parameters: {'name': '...'})\n"
            "  - 'get_manager': Get manager of an employee (parameters: {'employee_name': '...'})\n"
            "  - 'list_managers': List all managers (parameters: {})\n"
            "  - 'get_reports': List employees reporting to a manager (parameters: {'manager_name': '...'})\n"
            "- create_payment: Process payments (operation: 'create', parameters: {'vendor': '...', 'amount': <number>, 'currency': 'INR'})\n"
            "- calendar: Schedule events (operation: 'create_meeting', parameters: {'title': '...', 'time': '...', 'participant': '...'})\n"
            "- send_email: Send emails (operation: 'send_email', parameters: {'recipient': '...', 'subject': '...', 'body': '...'})\n"
            "- database: Database records (operation: 'read_record', 'update_record', or 'delete_record', parameters: {'target': 'customer_records', 'scope': 'all'|'single', 'all_records': true|false})\n\n"
            "CRITICAL RULES:\n"
            "- If the user's request is OUTSIDE the registered enterprise tools (for example: booking train/movie/flight tickets, general knowledge questions, definitions, algorithms, recipes, personal tasks, chit-chat, etc.), you MUST respond with JSON:\n"
            '  {"unsupported": true}\n'
            "- If the request matches a supported enterprise tool, respond ONLY with JSON:\n"
            '  {"tool": "<tool_name>", "operation": "<operation>", "parameters": { ... }}\n\n'
            "Respond ONLY with valid JSON."
        )

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        body = {
            "model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.0
        }

        default_base_url = "https://api.groq.com/openai/v1" if provider and provider.lower() == "groq" else "https://api.openai.com/v1"
        base_url = os.getenv("LLM_BASE_URL", default_base_url).rstrip("/")
        endpoint = f"{base_url}/chat/completions"

        with httpx.Client(timeout=10.0) as client:
            resp = client.post(endpoint, headers=headers, json=body)
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                parsed = json.loads(content.strip("`json\n"))
                if parsed.get("unsupported") is True or not parsed.get("tool") or str(parsed.get("tool")).lower() in ["none", "null", ""]:
                    return None

                tool = parsed.get("tool")
                operation = parsed.get("operation", "execute")
                params = parsed.get("parameters", {})

                # Normalize operation aliases
                if tool == "employee_data":
                    if operation in ["list", "list_names", "list_employees", "get_all", "get_all_employees"]:
                        operation = "search_employees"
                        if "query" in params and any(w in str(params["query"]).lower() for w in ["all", "employee", "names", "directory", "everyone"]):
                            params = {}
                elif tool == "calendar" and operation in ["schedule", "schedule_meeting", "create"]:
                    operation = "create_meeting"
                elif tool == "database":
                    if operation in ["delete", "bulk_delete"]:
                        operation = "delete_record"
                    elif operation in ["read", "get", "fetch"]:
                        operation = "read_record"
                elif tool == "create_payment" and operation in ["pay", "make_payment", "transfer"]:
                    operation = "create"
                elif tool == "send_email" and operation in ["send", "mail"]:
                    operation = "send_email"

                if not tool_registry.is_valid_operation(tool, operation):
                    return None

                return ActionProposal(
                    action_id=action_id,
                    agent_id=self.agent_id,
                    session_id=session_id,
                    tool=tool,
                    operation=operation,
                    parameters=params,
                    requested_at=requested_at
                )
        return None

ai_agent_service = AIAgentService()

