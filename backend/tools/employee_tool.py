from typing import Dict, Any, List
from tools.base import BaseEnterpriseTool
from database.db import SessionLocal
from database.models import EmployeeDB

class EmployeeDataTool(BaseEnterpriseTool):
    @property
    def name(self) -> str:
        return "employee_data"

    @property
    def description(self) -> str:
        return "Access database-backed employee directory, manager assignments, and salary details."

    def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            if operation == "list_employees":
                employees = db.query(EmployeeDB).all()
                result = [
                    {
                        "employee_id": emp.employee_id,
                        "name": emp.name,
                        "department": emp.department,
                        "role": emp.role,
                        "salary": emp.salary,
                        "email": emp.email,
                        "manager_id": emp.manager_id,
                        "is_manager": emp.is_manager
                    }
                    for emp in employees
                ]
                return {"status": "SUCCESS", "count": len(result), "employees": result}

            elif operation == "get_employee":
                emp_id = parameters.get("employee_id")
                name = parameters.get("name")
                query = parameters.get("query")
                
                emp = None
                if emp_id:
                    emp = db.query(EmployeeDB).filter(EmployeeDB.employee_id == emp_id).first()
                elif name:
                    emp = db.query(EmployeeDB).filter(EmployeeDB.name.like(f"%{name}%")).first()
                elif query:
                    emp = db.query(EmployeeDB).filter(EmployeeDB.name.like(f"%{query}%")).first()
                
                if not emp:
                    search_term = name or query or emp_id or ""
                    emp = db.query(EmployeeDB).filter(
                        (EmployeeDB.name.like(f"%{search_term}%")) | 
                        (EmployeeDB.employee_id.like(f"%{search_term}%"))
                    ).first()
                
                if emp:
                    return {
                        "status": "SUCCESS",
                        "employee": {
                            "employee_id": emp.employee_id,
                            "name": emp.name,
                            "department": emp.department,
                            "role": emp.role,
                            "salary": emp.salary,
                            "email": emp.email,
                            "manager_id": emp.manager_id,
                            "is_manager": emp.is_manager
                        }
                    }
                return {"status": "NOT_FOUND", "message": f"Employee details not found for query parameters: {parameters}"}

            elif operation == "get_manager":
                emp_id = parameters.get("employee_id")
                name = parameters.get("name") or parameters.get("employee_name")
                
                emp = None
                if emp_id:
                    emp = db.query(EmployeeDB).filter(EmployeeDB.employee_id == emp_id).first()
                elif name:
                    emp = db.query(EmployeeDB).filter(EmployeeDB.name.like(f"%{name}%")).first()
                
                if not emp:
                    return {"status": "NOT_FOUND", "message": "Employee not found."}
                
                if not emp.manager_id:
                    return {
                        "status": "SUCCESS",
                        "employee": {"name": emp.name},
                        "manager": None
                    }
                
                mgr = db.query(EmployeeDB).filter(EmployeeDB.employee_id == emp.manager_id).first()
                if mgr:
                    return {
                        "status": "SUCCESS",
                        "employee": {"name": emp.name},
                        "manager": {
                            "employee_id": mgr.employee_id,
                            "name": mgr.name,
                            "role": mgr.role,
                            "department": mgr.department
                        }
                    }
                return {"status": "ERROR", "message": f"Manager ID '{emp.manager_id}' not found in database."}

            elif operation == "list_managers":
                managers = db.query(EmployeeDB).filter(EmployeeDB.is_manager == True).all()
                result = [
                    {
                        "employee_id": m.employee_id,
                        "name": m.name,
                        "role": m.role,
                        "department": m.department
                    }
                    for m in managers
                ]
                return {"status": "SUCCESS", "count": len(result), "managers": result}

            elif operation == "get_reports":
                mgr_id = parameters.get("manager_id")
                name = parameters.get("name") or parameters.get("manager_name")
                
                mgr = None
                if mgr_id:
                    mgr = db.query(EmployeeDB).filter(EmployeeDB.employee_id == mgr_id).first()
                elif name:
                    mgr = db.query(EmployeeDB).filter(EmployeeDB.name.like(f"%{name}%")).first()
                
                if not mgr:
                    return {"status": "NOT_FOUND", "message": "Manager not found."}
                
                reports = db.query(EmployeeDB).filter(EmployeeDB.manager_id == mgr.employee_id).all()
                result = [
                    {
                        "employee_id": r.employee_id,
                        "name": r.name,
                        "role": r.role,
                        "department": r.department
                    }
                    for r in reports
                ]
                return {
                    "status": "SUCCESS",
                    "manager": {"name": mgr.name},
                    "count": len(result),
                    "reports": result
                }

            elif operation == "search_employees":
                dept = parameters.get("department", "").lower()
                query = str(parameters.get("query", "")).lower()
                name = str(parameters.get("name", "")).lower()
                
                q = db.query(EmployeeDB)
                if dept:
                    q = q.filter(EmployeeDB.department.like(f"%{dept}%"))
                if name:
                    q = q.filter(EmployeeDB.name.like(f"%{name}%"))
                if query:
                    generic_keywords = ["give me", "show me", "list", "all", "employee", "names", "directory", "everyone", "find"]
                    is_generic = all(word in generic_keywords or len(word) < 3 for word in query.split())
                    if not is_generic:
                        search_words = [w for w in query.split() if w not in ["find", "employee", "the", "for", "named", "show", "me", "details", "of"]]
                        search_term = " ".join(search_words) if search_words else query
                        q = q.filter(
                            (EmployeeDB.name.like(f"%{search_term}%")) | 
                            (EmployeeDB.name.like(f"%{query}%")) | 
                            (EmployeeDB.role.like(f"%{query}%"))
                        )
                
                employees = q.all()
                result = [
                    {
                        "employee_id": emp.employee_id,
                        "name": emp.name,
                        "department": emp.department,
                        "role": emp.role,
                        "salary": emp.salary,
                        "email": emp.email,
                        "manager_id": emp.manager_id,
                        "is_manager": emp.is_manager
                    }
                    for emp in employees
                ]
                return {"status": "SUCCESS", "count": len(result), "employees": result}

            return {"status": "ERROR", "message": f"Unsupported operation '{operation}' for employee_data tool."}
        
        finally:
            db.close()
