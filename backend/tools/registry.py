from typing import Dict, Any, List
from tools.base import BaseEnterpriseTool
from tools.email_tool import EmailTool
from tools.employee_tool import EmployeeDataTool
from tools.payment_tool import PaymentTool
from tools.database_tool import DatabaseTool
from tools.calendar_tool import CalendarTool

SUPPORTED_OPERATIONS: Dict[str, List[str]] = {
    "calendar": ["create", "create_meeting", "update", "update_meeting", "cancel", "cancel_meeting"],
    "create_payment": ["create"],
    "send_email": ["send_email"],
    "employee_data": ["list_employees", "get_employee", "get_manager", "list_managers", "get_reports", "search_employees"],
    "database": ["read_record", "update_record", "delete_record"]
}

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseEnterpriseTool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        tools = [
            EmailTool(),
            EmployeeDataTool(),
            PaymentTool(),
            DatabaseTool(),
            CalendarTool()
        ]
        for tool in tools:
            self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseEnterpriseTool:
        return self._tools.get(name)

    def is_valid_operation(self, tool_name: str, operation: str) -> bool:
        if tool_name not in self._tools:
            return False
        valid_ops = SUPPORTED_OPERATIONS.get(tool_name, [])
        return operation in valid_ops

    def execute_tool(self, tool_name: str, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        tool = self.get_tool(tool_name)
        if not tool:
            return {"status": "ERROR", "message": f"Tool '{tool_name}' is not registered in enterprise environment."}
        if not self.is_valid_operation(tool_name, operation):
            return {"status": "ERROR", "message": f"Unsupported operation '{operation}' for {tool_name} tool."}
        return tool.execute(operation, parameters)

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": name,
                "description": tool.description,
                "supported_operations": SUPPORTED_OPERATIONS.get(name, [])
            }
            for name, tool in self._tools.items()
        ]

tool_registry = ToolRegistry()

