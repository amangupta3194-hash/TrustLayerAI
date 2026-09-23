from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ActionProposal(BaseModel):
    action_id: str = Field(..., example="ACT-98214")
    agent_id: str = Field(default="trustops-agent", example="trustops-agent")
    session_id: str = Field(..., example="SES-10293")
    tool: str = Field(..., example="create_payment")
    operation: str = Field(..., example="create")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    requested_at: str = Field(..., example="2026-08-13T23:50:00Z")

class PolicyCheckResult(BaseModel):
    policy_id: str
    policy_name: str
    status: str              # PASS, REQUIRE_APPROVAL, BLOCK
    severity: str            # LOW, MEDIUM, HIGH, CRITICAL
    message: str

class RiskAssessmentResult(BaseModel):
    score: int               # 0 - 100
    level: str               # LOW, MEDIUM, HIGH
    factors: Dict[str, Any]
    explanation: str

class GovernanceDecisionResult(BaseModel):
    action_id: str
    decision: str            # ALLOW, REQUIRE_APPROVAL, BLOCK
    risk: RiskAssessmentResult
    policy_checks: List[PolicyCheckResult]
    explanation: str
    status: str              # ALLOWED, PENDING_APPROVAL, BLOCKED

class ChatRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    user_prompt: str
    action_proposal: Optional[ActionProposal] = None
    governance: Optional[GovernanceDecisionResult] = None
    tool_result: Optional[Dict[str, Any]] = None
    final_response: str

class ApprovalAction(BaseModel):
    reviewer_notes: Optional[str] = None
