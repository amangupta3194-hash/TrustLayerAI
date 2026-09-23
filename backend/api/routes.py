import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.db import get_db
from database.models import ActionProposalDB, PolicyDB, RiskAssessmentDB, ApprovalDB, AuditLogDB
from models.schemas import (
    ChatRequest, ChatResponse, ActionProposal, GovernanceDecisionResult, ApprovalAction
)
from agent.llm_agent import ai_agent_service
from trustlayer.service import trustlayer_service
from tools.registry import tool_registry

router = APIRouter(prefix="/api")

@router.get("/health")
def get_health(db: Session = Depends(get_db)):
    try:
        # Check DB connectivity
        db.query(PolicyDB).first()
        db_status = "CONNECTED"
    except Exception:
        db_status = "ERROR"

    return {
        "status": "HEALTHY" if db_status == "CONNECTED" else "DEGRADED",
        "components": {
            "backend_api": "ONLINE",
            "trustlayer": "ACTIVE",
            "database": db_status,
            "ai_agent": "READY"
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_actions = db.query(ActionProposalDB).count()
    allowed_count = db.query(ActionProposalDB).filter(
        (ActionProposalDB.decision == "ALLOW") | (ActionProposalDB.status.in_(["ALLOWED", "EXECUTED"]))
    ).count()
    
    pending_approval_count = db.query(ApprovalDB).filter(ApprovalDB.status == "PENDING").count()
    
    blocked_count = db.query(ActionProposalDB).filter(
        (ActionProposalDB.decision == "BLOCK") | (ActionProposalDB.status == "BLOCKED")
    ).count()

    avg_risk = db.query(func.avg(ActionProposalDB.risk_score)).scalar()
    avg_risk_score = round(float(avg_risk), 1) if avg_risk is not None else 0.0

    return {
        "total_actions": total_actions,
        "allowed_count": allowed_count,
        "pending_approval_count": pending_approval_count,
        "blocked_count": blocked_count,
        "average_risk_score": avg_risk_score
    }

# Demo reset endpoint – clears demo data (actions, approvals, audit logs, risk assessments)
@router.post("/demo/reset")
def reset_demo_data(db: Session = Depends(get_db)):
    # Delete all rows from mutable tables
    db.query(ActionProposalDB).delete()
    db.query(ApprovalDB).delete()
    db.query(AuditLogDB).delete()
    db.query(RiskAssessmentDB).delete()
    db.commit()
    return {"status": "RESET", "message": "Demo data cleared."}

@router.get("/dashboard/risk-distribution")
def get_risk_distribution(db: Session = Depends(get_db)):
    low_count = db.query(ActionProposalDB).filter(ActionProposalDB.risk_level == "LOW").count()
    med_count = db.query(ActionProposalDB).filter(ActionProposalDB.risk_level == "MEDIUM").count()
    high_count = db.query(ActionProposalDB).filter(ActionProposalDB.risk_level == "HIGH").count()

    avg_risk = db.query(func.avg(ActionProposalDB.risk_score)).scalar()
    avg_score = round(float(avg_risk), 1) if avg_risk is not None else 0.0

    highest_act = db.query(ActionProposalDB).order_by(ActionProposalDB.risk_score.desc()).first()
    highest_action = None
    if highest_act:
        highest_action = {
            "action_id": highest_act.action_id,
            "tool": highest_act.tool,
            "operation": highest_act.operation,
            "user_prompt": highest_act.user_prompt,
            "risk_score": highest_act.risk_score,
            "risk_level": highest_act.risk_level,
            "decision": highest_act.decision,
            "reason": highest_act.reason
        }

    return {
        "low_risk": low_count,
        "medium_risk": med_count,
        "high_risk": high_count,
        "average_score": avg_score,
        "highest_risk_action": highest_action
    }

@router.get("/dashboard/decisions")
def get_decision_distribution(db: Session = Depends(get_db)):
    allow_count = db.query(ActionProposalDB).filter(ActionProposalDB.decision == "ALLOW").count()
    approval_count = db.query(ActionProposalDB).filter(ActionProposalDB.decision == "REQUIRE_APPROVAL").count()
    block_count = db.query(ActionProposalDB).filter(ActionProposalDB.decision == "BLOCK").count()

    return {
        "ALLOW": allow_count,
        "REQUIRE_APPROVAL": approval_count,
        "BLOCK": block_count
    }

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt must not be empty.")
    return ai_agent_service.process_user_request(request.prompt, request.session_id, db)

@router.post("/actions/evaluate", response_model=GovernanceDecisionResult)
def evaluate_action_endpoint(proposal: ActionProposal, user_prompt: Optional[str] = "Direct API Action Evaluation", db: Session = Depends(get_db)):
    return trustlayer_service.evaluate_and_record(proposal, user_prompt, db)

@router.get("/actions")
def get_actions(limit: int = 50, db: Session = Depends(get_db)):
    actions = db.query(ActionProposalDB).order_by(ActionProposalDB.requested_at.desc()).limit(limit).all()
    results = []
    for act in actions:
        results.append({
            "action_id": act.action_id,
            "agent_id": act.agent_id,
            "session_id": act.session_id,
            "tool": act.tool,
            "operation": act.operation,
            "parameters": json.loads(act.parameters_json) if act.parameters_json else {},
            "requested_at": act.requested_at,
            "status": act.status,
            "risk_score": act.risk_score,
            "risk_level": act.risk_level,
            "decision": act.decision,
            "reason": act.reason,
            "user_prompt": act.user_prompt,
            "execution_result": json.loads(act.execution_result_json) if act.execution_result_json else None
        })
    return results

@router.get("/actions/{action_id}")
def get_action_detail(action_id: str, db: Session = Depends(get_db)):
    act = db.query(ActionProposalDB).filter(ActionProposalDB.action_id == action_id).first()
    if not act:
        raise HTTPException(status_code=404, detail=f"Action proposal '{action_id}' not found.")

    risk_db = db.query(RiskAssessmentDB).filter(RiskAssessmentDB.action_id == action_id).first()
    approval_db = db.query(ApprovalDB).filter(ApprovalDB.action_id == action_id).first()
    audit_logs = db.query(AuditLogDB).filter(AuditLogDB.action_id == action_id).order_by(AuditLogDB.id.asc()).all()

    # Build step-by-step lifecycle timeline
    timeline = []
    
    # 1. Action Requested
    timeline.append({
        "step": 1,
        "title": "Action Proposal Generated",
        "actor": "AI AGENT",
        "timestamp": act.requested_at,
        "status": "COMPLETED",
        "explanation": f"AI Agent generated proposal for tool '{act.tool}' ({act.operation})."
    })

    # 2. Policy Evaluation & Risk Assessment
    timeline.append({
        "step": 2,
        "title": "TrustLayer Governance Check",
        "actor": "TRUSTLAYER",
        "timestamp": act.requested_at,
        "status": "COMPLETED",
        "explanation": f"Evaluated security policies and calculated risk score of {act.risk_score}/100 ({act.risk_level})."
    })

    # 3. Governance Decision
    timeline.append({
        "step": 3,
        "title": "Decision Synthesized",
        "actor": "TRUSTLAYER",
        "timestamp": act.requested_at,
        "status": "COMPLETED",
        "explanation": act.reason or f"Decision: {act.decision}"
    })

    # 4. Human Approval (If applicable)
    if approval_db:
        timeline.append({
            "step": 4,
            "title": "Human Authorization",
            "actor": "HUMAN_OPERATOR",
            "timestamp": approval_db.decided_at or approval_db.requested_at,
            "status": approval_db.status,
            "explanation": f"Approval Status: {approval_db.status}. Notes: {approval_db.reviewer_notes or 'Pending review'}"
        })

    # 5. Tool Execution
    tool_status = "EXECUTED" if act.status == "EXECUTED" else ("BLOCKED" if act.status == "BLOCKED" else "PENDING")
    timeline.append({
        "step": 5,
        "title": "Tool Execution Gateway",
        "actor": "TRUSTLAYER_GATEWAY",
        "timestamp": act.requested_at,
        "status": tool_status,
        "explanation": f"Execution status: {tool_status}."
    })

    formatted_audits = []
    for log in audit_logs:
        formatted_audits.append({
            "id": log.id,
            "event_type": log.event_type,
            "actor": log.actor,
            "details": json.loads(log.details_json) if log.details_json else {},
            "timestamp": log.timestamp
        })

    return {
        "action_id": act.action_id,
        "agent_id": act.agent_id,
        "session_id": act.session_id,
        "tool": act.tool,
        "operation": act.operation,
        "parameters": json.loads(act.parameters_json) if act.parameters_json else {},
        "requested_at": act.requested_at,
        "status": act.status,
        "risk_score": act.risk_score,
        "risk_level": act.risk_level,
        "decision": act.decision,
        "reason": act.reason,
        "user_prompt": act.user_prompt,
        "execution_result": json.loads(act.execution_result_json) if act.execution_result_json else None,
        "risk_factors": json.loads(risk_db.factors_json) if risk_db and risk_db.factors_json else {},
        "approval": {
            "status": approval_db.status,
            "requested_at": approval_db.requested_at,
            "decided_at": approval_db.decided_at,
            "notes": approval_db.reviewer_notes
        } if approval_db else None,
        "timeline": timeline,
        "audit_logs": formatted_audits
    }

@router.get("/audit")
def get_audit_logs(
    action_id: Optional[str] = None,
    decision: Optional[str] = None,
    tool: Optional[str] = None,
    risk_level: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(AuditLogDB)
    if action_id:
        query = query.filter(AuditLogDB.action_id == action_id)
    if search:
        s = f"%{search}%"
        query = query.filter(
            (AuditLogDB.action_id.like(s)) |
            (AuditLogDB.event_type.like(s)) |
            (AuditLogDB.actor.like(s)) |
            (AuditLogDB.details_json.like(s))
        )
    
    logs = query.order_by(AuditLogDB.id.desc()).limit(limit).all()
    results = []
    for log in logs:
        details = json.loads(log.details_json) if log.details_json else {}
        results.append({
            "id": log.id,
            "action_id": log.action_id,
            "event_type": log.event_type,
            "actor": log.actor,
            "details": details,
            "timestamp": log.timestamp
        })
    return results

@router.post("/audit/clear")
def clear_audit_logs(db: Session = Depends(get_db)):
    try:
        db.query(AuditLogDB).delete()
        db.commit()
        return {"status": "SUCCESS", "message": "Audit logs cleared successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear audit logs: {str(e)}")

@router.get("/approvals")
def get_pending_approvals(db: Session = Depends(get_db)):
    approvals = db.query(ApprovalDB).filter(ApprovalDB.status == "PENDING").all()
    results = []
    for app in approvals:
        act = db.query(ActionProposalDB).filter(ActionProposalDB.action_id == app.action_id).first()
        results.append({
            "approval_id": app.id,
            "action_id": app.action_id,
            "status": app.status,
            "requested_at": app.requested_at,
            "action_details": {
                "agent_id": act.agent_id if act else None,
                "tool": act.tool if act else None,
                "operation": act.operation if act else None,
                "parameters": json.loads(act.parameters_json) if act and act.parameters_json else {},
                "risk_score": act.risk_score if act else None,
                "risk_level": act.risk_level if act else None,
                "reason": act.reason if act else None,
                "user_prompt": act.user_prompt if act else None
            }
        })
    return results

@router.post("/approvals/{action_id}/approve")
def approve_action(action_id: str, payload: Optional[ApprovalAction] = None, db: Session = Depends(get_db)):
    approval = db.query(ApprovalDB).filter(ApprovalDB.action_id == action_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail=f"No pending approval found for action '{action_id}'.")
    
    if approval.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Approval for action '{action_id}' is already {approval.status}.")

    act = db.query(ActionProposalDB).filter(ActionProposalDB.action_id == action_id).first()
    if not act:
        raise HTTPException(status_code=404, detail=f"Action proposal '{action_id}' not found.")

    # 1. Update Approval DB
    now_iso = datetime.utcnow().isoformat() + "Z"
    notes = payload.reviewer_notes if payload else "Approved by Human Governance Operator."
    approval.status = "APPROVED"
    approval.decided_at = now_iso
    approval.reviewer_notes = notes

    # 2. Execute approved tool through TrustLayer path ONLY now
    params = json.loads(act.parameters_json) if act.parameters_json else {}
    tool_result = tool_registry.execute_tool(act.tool, act.operation, params)

    # 3. Update Action DB & Audit Log
    act.status = "EXECUTED"
    act.execution_result_json = json.dumps(tool_result)

    audit_1 = AuditLogDB(
        action_id=action_id,
        event_type="APPROVAL_GRANTED",
        actor="HUMAN_OPERATOR",
        details_json=json.dumps({"notes": notes}),
        timestamp=now_iso
    )
    audit_2 = AuditLogDB(
        action_id=action_id,
        event_type="TOOL_EXECUTED",
        actor="TRUSTLAYER_GATEWAY",
        details_json=json.dumps(tool_result),
        timestamp=now_iso
    )
    db.add(audit_1)
    db.add(audit_2)
    db.commit()

    return {
        "status": "APPROVED",
        "action_id": action_id,
        "tool_result": tool_result,
        "message": f"Action '{action_id}' approved and tool executed successfully."
    }

@router.post("/approvals/{action_id}/reject")
def reject_action(action_id: str, payload: Optional[ApprovalAction] = None, db: Session = Depends(get_db)):
    approval = db.query(ApprovalDB).filter(ApprovalDB.action_id == action_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail=f"No pending approval found for action '{action_id}'.")

    if approval.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Approval for action '{action_id}' is already {approval.status}.")

    act = db.query(ActionProposalDB).filter(ActionProposalDB.action_id == action_id).first()

    now_iso = datetime.utcnow().isoformat() + "Z"
    notes = payload.reviewer_notes if payload else "Rejected by Human Governance Operator."

    approval.status = "REJECTED"
    approval.decided_at = now_iso
    approval.reviewer_notes = notes

    if act:
        act.status = "REJECTED"

    audit = AuditLogDB(
        action_id=action_id,
        event_type="APPROVAL_REJECTED",
        actor="HUMAN_OPERATOR",
        details_json=json.dumps({"notes": notes}),
        timestamp=now_iso
    )
    db.add(audit)
    db.commit()

    return {
        "status": "REJECTED",
        "action_id": action_id,
        "message": f"Action '{action_id}' was rejected by human operator. Tool execution prevented."
    }

@router.delete("/approvals/{action_id}")
def delete_approval(action_id: str, db: Session = Depends(get_db)):
    approval = db.query(ApprovalDB).filter(ApprovalDB.action_id == action_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail=f"No approval record found for action '{action_id}'.")
    
    act = db.query(ActionProposalDB).filter(ActionProposalDB.action_id == action_id).first()
    if act:
        act.status = "REJECTED"

    db.delete(approval)
    
    now_iso = datetime.utcnow().isoformat() + "Z"
    audit = AuditLogDB(
        action_id=action_id,
        event_type="APPROVAL_REMOVED",
        actor="HUMAN_OPERATOR",
        details_json=json.dumps({"info": "Pending approval request removed/deleted by operator."}),
        timestamp=now_iso
    )
    db.add(audit)
    db.commit()
    return {"status": "DELETED", "message": f"Approval request for action '{action_id}' has been removed."}

@router.get("/policies")
def get_policies(db: Session = Depends(get_db)):
    policies = db.query(PolicyDB).all()
    return [
        {
            "policy_id": p.policy_id,
            "policy_name": p.policy_name,
            "description": p.description,
            "severity": p.severity,
            "action_on_violation": p.action_on_violation,
            "is_active": p.is_active
        }
        for p in policies
    ]

@router.get("/tools")
def get_tools():
    return tool_registry.get_tools_schema()
