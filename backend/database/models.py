import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime
from database.db import Base

class ActionProposalDB(Base):
    __tablename__ = "actions"

    action_id = Column(String, primary_key=True, index=True)
    agent_id = Column(String, nullable=False, default="trustops-agent")
    session_id = Column(String, nullable=False)
    tool = Column(String, nullable=False)
    operation = Column(String, nullable=False)
    parameters_json = Column(Text, nullable=False)
    requested_at = Column(String, nullable=False)
    
    # Governance outputs
    status = Column(String, nullable=False, default="PENDING")  # PENDING, ALLOWED, REQUIRE_APPROVAL, BLOCKED, EXECUTED, REJECTED
    risk_score = Column(Integer, nullable=True)
    risk_level = Column(String, nullable=True)                  # LOW, MEDIUM, HIGH
    decision = Column(String, nullable=True)                    # ALLOW, REQUIRE_APPROVAL, BLOCK
    reason = Column(Text, nullable=True)
    execution_result_json = Column(Text, nullable=True)
    user_prompt = Column(Text, nullable=True)

class PolicyDB(Base):
    __tablename__ = "policies"

    policy_id = Column(String, primary_key=True, index=True)
    policy_name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String, nullable=False)                  # LOW, MEDIUM, HIGH, CRITICAL
    action_on_violation = Column(String, nullable=False)        # REQUIRE_APPROVAL, BLOCK
    is_active = Column(Boolean, default=True)

class RiskAssessmentDB(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action_id = Column(String, nullable=False, index=True)
    score = Column(Integer, nullable=False)
    level = Column(String, nullable=False)
    factors_json = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    created_at = Column(String, nullable=False)

class ApprovalDB(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action_id = Column(String, nullable=False, unique=True, index=True)
    status = Column(String, nullable=False, default="PENDING")  # PENDING, APPROVED, REJECTED
    requested_at = Column(String, nullable=False)
    decided_at = Column(String, nullable=True)
    reviewer_notes = Column(Text, nullable=True)

class AuditLogDB(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action_id = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    actor = Column(String, nullable=False)
    details_json = Column(Text, nullable=False)
    timestamp = Column(String, nullable=False)

class EmployeeDB(Base):
    __tablename__ = "employees"

    employee_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    role = Column(String, nullable=False)
    salary = Column(String, nullable=False)
    email = Column(String, nullable=False)
    manager_id = Column(String, nullable=True)
    is_manager = Column(Boolean, default=False)
