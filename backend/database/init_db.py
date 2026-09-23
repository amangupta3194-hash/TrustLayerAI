from database.db import engine, Base, SessionLocal
from database.models import PolicyDB, EmployeeDB

INITIAL_POLICIES = [
    {
        "policy_id": "P-001",
        "policy_name": "Payment Threshold",
        "description": "Payments above ₹10,000 require human approval.",
        "severity": "HIGH",
        "action_on_violation": "REQUIRE_APPROVAL",
        "is_active": True,
    },
    {
        "policy_id": "P-002",
        "policy_name": "Confidential External Data",
        "description": "Sensitive employee information must not be sent to external recipients.",
        "severity": "CRITICAL",
        "action_on_violation": "BLOCK",
        "is_active": True,
    },
    {
        "policy_id": "P-003",
        "policy_name": "Destructive Database Operation",
        "description": "Bulk deletion of customer records is prohibited.",
        "severity": "CRITICAL",
        "action_on_violation": "BLOCK",
        "is_active": True,
    },
    {
        "policy_id": "P-004",
        "policy_name": "Sensitive Employee Data",
        "description": "Salary information requires elevated authorization.",
        "severity": "MEDIUM",
        "action_on_violation": "REQUIRE_APPROVAL",
        "is_active": True,
    },
    {
        "policy_id": "P-005",
        "policy_name": "Bulk Operations",
        "description": "Operations affecting more than 100 records require human approval.",
        "severity": "MEDIUM",
        "action_on_violation": "REQUIRE_APPROVAL",
        "is_active": True,
    },
    {
        "policy_id": "P-006",
        "policy_name": "Agent Tool Permission",
        "description": "Agents may only use tools assigned to their role.",
        "severity": "HIGH",
        "action_on_violation": "BLOCK",
        "is_active": True,
    },
]

INITIAL_EMPLOYEES = [
    {
        "employee_id": "EMP-101",
        "name": "Alice Smith",
        "department": "HR",
        "role": "HR Manager",
        "salary": "₹1,20,000 / month",
        "email": "alice.smith@company.com",
        "manager_id": "EMP-104",
        "is_manager": True
    },
    {
        "employee_id": "EMP-102",
        "name": "Bob Jones",
        "department": "Engineering",
        "role": "Lead Architect",
        "salary": "₹1,80,000 / month",
        "email": "bob.jones@company.com",
        "manager_id": "EMP-104",
        "is_manager": True
    },
    {
        "employee_id": "EMP-103",
        "name": "Carol White",
        "department": "Sales",
        "role": "Account Executive",
        "salary": "₹95,000 / month",
        "email": "carol.white@company.com",
        "manager_id": "EMP-104",
        "is_manager": False
    },
    {
        "employee_id": "EMP-104",
        "name": "David Brown",
        "department": "Finance",
        "role": "Financial Analyst",
        "salary": "₹1,10,000 / month",
        "email": "david.brown@company.com",
        "manager_id": None,
        "is_manager": True
    }
]

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for pol_data in INITIAL_POLICIES:
            existing = db.query(PolicyDB).filter(PolicyDB.policy_id == pol_data["policy_id"]).first()
            if not existing:
                policy = PolicyDB(**pol_data)
                db.add(policy)
        
        for emp_data in INITIAL_EMPLOYEES:
            existing = db.query(EmployeeDB).filter(EmployeeDB.employee_id == emp_data["employee_id"]).first()
            if not existing:
                emp = EmployeeDB(**emp_data)
                db.add(emp)
                
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized and policies seeded successfully.")
