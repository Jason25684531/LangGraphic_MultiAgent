from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import StructuredTool

from studio.skills.loader import load_skill as default_load_skill, load_skill_metadata
from studio.tools.registry import resolve_tools


def run_agent_loop(model, messages, tools, max_turns: int = 8):
    tools_by_name = {tool.name: tool for tool in tools}
    for _ in range(max_turns):
        message = model.invoke(messages)
        calls = getattr(message, "tool_calls", [])
        if not calls:
            return message.content if hasattr(message, "content") else str(message)
        messages.append(message)
        for call in calls:
            tool = tools_by_name.get(call["name"])
            try:
                content = str(tool.invoke(call["args"])) if tool else f"Unknown tool: {call['name']}"
            except Exception as exc:
                content = f"Tool failed: {exc}"
            messages.append(ToolMessage(content=content, tool_call_id=call["id"]))
    return "Agent stopped after reaching the tool-call limit."


class RoleAgent:
    def __init__(self, model, prompt, tools):
        self.model, self.prompt, self.tools = model, prompt, tools

    def invoke(self, task: str):
        return run_agent_loop(self.model, [HumanMessage(content=f"{self.prompt}\n\nTask: {task}")], self.tools)


def create_role_agent(role_config, model, tool_registry=None, skill_loader=default_load_skill):
    registry = tool_registry or __import__("studio.tools.registry", fromlist=["TOOL_REGISTRY"]).TOOL_REGISTRY
    tools = resolve_tools(role_config.tools, registry)
    allowed = set(role_config.skills)

    def load_allowed_skill(name: str) -> str:
        if name not in allowed:
            raise ValueError(f"Skill not allowed for {role_config.name}: {name}")
        return skill_loader(name)

    tools.append(StructuredTool.from_function(load_allowed_skill, name="load_skill", description="Load an allowed role skill."))
    bound = model.bind_tools(tools) if hasattr(model, "bind_tools") else model
    metadata = [load_skill_metadata(skill) for skill in role_config.skills]
    skills = ", ".join(f"{item.name}: {item.description}" for item in metadata) or "none"
    prompt = f"{role_config.system_prompt}\nAvailable skills (load on demand): {skills}"
    return RoleAgent(bound, prompt, tools)
