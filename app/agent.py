from typing import Any, Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.prebuilt import create_react_agent

from app.config import settings
from app.tools.data_tools import (
    analyze_dataset_statistics,
    run_dataset_outlier_detection,
    execute_dataframe_query,
)
from app.tools.system_tools import calculate_custom_metric, task_scheduler_mock


class AIForgeAgentService:
    """OOP Agent Orchestrator handling tool execution and context."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.MODEL_NAME,
            temperature=settings.TEMPERATURE,
            api_key=settings.OPENAI_API_KEY,
        )
        self.tools = [
            analyze_dataset_statistics,
            run_dataset_outlier_detection,
            execute_dataframe_query,
            calculate_custom_metric,
            task_scheduler_mock,
        ]
        self.system_prompt = (
            "You are AIForge, an intelligent task automation and data analysis agent. "
            "You have access to structured data pipelines (Pandas/NumPy) and automation tools. "
            "Use tools whenever calculations, data queries, or task executions are requested."
        )
        self.agent_executor = create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=self.system_prompt,
        )

    def _convert_mongo_history_to_messages(self, history: List[Dict[str, Any]]) -> List[Any]:
        messages = []
        for msg in history:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
        return messages

    async def run(
        self,
        session_id: str,
        user_input: str,
        history_records: List[Dict[str, Any]],
        dataset_filepath: str = None,
    ) -> Dict[str, Any]:
        messages = self._convert_mongo_history_to_messages(history_records)

        current_prompt = user_input
        if dataset_filepath:
            current_prompt += f"\n[Context: Active dataset path is '{dataset_filepath}']"

        messages.append(HumanMessage(content=current_prompt))

        result = await self.agent_executor.ainvoke({"messages": messages})
        final_messages = result.get("messages", [])
        final_answer = "Could not generate a response."
        executed_steps = []

        for m in final_messages:
            if isinstance(m, ToolMessage):
                executed_steps.append(f"Tool `{m.name}` executed.")
            elif isinstance(m, AIMessage) and m.content:
                final_answer = m.content

        return {
            "output": final_answer,
            "steps": executed_steps,
        }


agent_service = AIForgeAgentService()