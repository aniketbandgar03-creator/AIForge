import json
import datetime
from langchain_core.tools import tool


@tool
def calculate_custom_metric(formula: str) -> str:
    """Calculates mathematical expressions and KPI derivations safely."""
    allowed_chars = set("0123456789+-*/(). %e")
    if not all(c in allowed_chars for c in formula):
        return json.dumps({"error": "Formula contains unsupported characters"})
    try:
        result = eval(formula, {"__builtins__": None}, {})
        return json.dumps({"formula": formula, "result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def task_scheduler_mock(task_name: str, execute_at: str) -> str:
    """Mock task scheduler for automated jobs or alert triggers."""
    return json.dumps({
        "status": "scheduled",
        "task_name": task_name,
        "execute_at": execute_at,
        "scheduled_time": datetime.datetime.now().isoformat(),
    })