from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import StructuredTool
from pydantic import BaseModel

from studio.agents.factory import create_role_agent, run_agent_loop
from studio.roles.loader import UnknownRoleError
from studio.state import DelegationRecord


class DelegationResult(BaseModel):
    role: str
    task: str
    ok: bool
    result: str = ""
    error: str | None = None


class Supervisor:
    def __init__(self, registry, model, tool_registry, skill_loader):
        self.registry, self.model = registry, model
        self.tool_registry, self.skill_loader = tool_registry, skill_loader
        self.cache: dict[str, object] = {}
        self.delegations: list[DelegationRecord] = []
        self.prompt = "You are the Studio Supervisor. For every request, first delegate work to at least one suitable specialist with delegate_task, then synthesize its result. Available specialists:\n" + "\n".join(
            f"- {role.name}: {role.description}" for role in registry
        )
        self.delegate_tool = StructuredTool.from_function(
            self.delegate_task, name="delegate_task", description="Delegate a task to an available specialist."
        )
        self.agent_model = model.bind_tools([self.delegate_tool]) if hasattr(model, "bind_tools") else model

    def delegate_task(self, role: str, task: str) -> DelegationResult:
        try:
            config = self.registry.get(role)
        except UnknownRoleError:
            result = DelegationResult(role=role, task=task, ok=False, error=f"Unknown role: {role}")
            self.delegations.append({"role": role, "task": task, "ok": False, "error": result.error})
            return result
        agent = self.cache.setdefault(role, create_role_agent(config, self.model, self.tool_registry, self.skill_loader))
        try:
            result = agent.invoke(task)
            self.delegations.append({"role": role, "task": task, "ok": True})
            return DelegationResult(role=role, task=task, ok=True, result=result)
        except Exception as exc:
            error = str(exc)
            self.delegations.append({"role": role, "task": task, "ok": False, "error": error})
            return DelegationResult(role=role, task=task, ok=False, error=error)

    def invoke(self, task: str, max_turns: int = 8) -> tuple[str, list[DelegationRecord]]:
        self.delegations = []
        result = run_agent_loop(
            self.agent_model,
            [SystemMessage(content=self.prompt), HumanMessage(content=task)],
            [self.delegate_tool],
            max_turns,
        )
        return result, self.delegations.copy()
