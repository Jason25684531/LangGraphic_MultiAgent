from studio.agents.factory import create_role_agent
from studio.roles.loader import UnknownRoleError


class Supervisor:
    def __init__(self, registry, model, tool_registry, skill_loader):
        self.registry, self.model = registry, model
        self.tool_registry, self.skill_loader = tool_registry, skill_loader
        self.cache, self.delegations = {}, []
        self.prompt = "Available roles: " + ", ".join(role.name for role in registry)

    def delegate_task(self, role: str, task: str) -> str:
        try:
            config = self.registry.get(role)
        except UnknownRoleError:
            self.delegations.append({"role": role, "task": task, "ok": False})
            return f"Unknown role: {role}"
        agent = self.cache.setdefault(role, create_role_agent(config, self.model, self.tool_registry, self.skill_loader))
        try:
            result = agent.invoke(task)
            self.delegations.append({"role": role, "task": task, "ok": True})
            return result
        except Exception as exc:
            self.delegations.append({"role": role, "task": task, "ok": False})
            return f"Delegation failed: {exc}"
