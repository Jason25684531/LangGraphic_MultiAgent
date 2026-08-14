from langchain_core.messages import ToolMessage
from langchain_core.tools import StructuredTool

from studio.skills.loader import load_skill as default_load_skill
from studio.tools.registry import resolve_tools


class RoleAgent:
    def __init__(self, model, prompt, tools):
        self.model, self.prompt, self.tools = model, prompt, tools

    def invoke(self, task: str):
        prompt = f"{self.prompt}\n\nTask: {task}"
        message = self.model.invoke(prompt)
        tools = {tool.name: tool for tool in self.tools}
        # ponytail: one short local tool loop; use a full agent executor only when multi-step planning is needed.
        for _ in range(1):
            calls = getattr(message, "tool_calls", [])
            if not calls:
                break
            replies = [ToolMessage(content=str(tools[call["name"]].invoke(call["args"])), tool_call_id=call["id"])
                       for call in calls if call["name"] in tools]
            message = self.model.invoke([prompt, message, *replies])
        return message.content if hasattr(message, "content") else str(message)


def create_role_agent(role_config, model, tool_registry=None, skill_loader=default_load_skill):
    registry = tool_registry or __import__("studio.tools.registry", fromlist=["TOOL_REGISTRY"]).TOOL_REGISTRY
    for skill in role_config.skills:
        skill_loader(skill)
    tools = resolve_tools(role_config.tools, registry)
    allowed = set(role_config.skills)

    def load_allowed_skill(name: str) -> str:
        if name not in allowed:
            raise ValueError(f"Skill not allowed for {role_config.name}: {name}")
        return skill_loader(name)

    tools.append(StructuredTool.from_function(load_allowed_skill, name="load_skill", description="Load an allowed role skill."))
    bound = model.bind_tools(tools) if hasattr(model, "bind_tools") else model
    prompt = f"{role_config.system_prompt}\nAvailable skills (load on demand): {', '.join(role_config.skills) or 'none'}"
    return RoleAgent(bound, prompt, tools)
