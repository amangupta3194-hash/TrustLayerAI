from datetime import datetime
from models.schemas import ActionProposal

class ActionMonitor:
    def capture_action(self, proposal: ActionProposal) -> dict:
        """
        Captures and normalizes structured action proposal details for TrustLayer inspection.
        """
        return {
            "action_id": proposal.action_id,
            "agent_id": proposal.agent_id,
            "session_id": proposal.session_id,
            "tool": proposal.tool,
            "operation": proposal.operation,
            "parameters": proposal.parameters,
            "captured_at": datetime.utcnow().isoformat() + "Z"
        }

action_monitor = ActionMonitor()
