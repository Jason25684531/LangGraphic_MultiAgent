import pytest
from langchain_core.messages import AIMessage
from studio.agents.factory import create_role_agent
from studio.roles.loader import RoleRegistry
from studio.testing import FakeChatModel
from studio.tools.registry import TOOL_REGISTRY


def test_role_agent_is_injected_and_scoped():
    role = RoleRegistry("src/studio/roles").get("strategist")
    model = FakeChatModel(["draft"])
    agent = create_role_agent(role, model, TOOL_REGISTRY)
    assert agent.invoke("task") == "draft"
    assert "brand-strategy" in agent.prompt
    assert role.system_prompt in agent.prompt
    for skill in role.skills:
        metadata = __import__("studio.skills.loader", fromlist=["load_skill_metadata"]).load_skill_metadata(skill)
        assert metadata.name in agent.prompt and metadata.description in agent.prompt
        assert "## Process" not in agent.prompt
    assert {tool.name for tool in agent.tools} == {"word_count", "load_skill"}


def test_unknown_tool_fails():
    role = RoleRegistry("src/studio/roles").get("strategist").model_copy(update={"tools": ["nope"]})
    with pytest.raises(KeyError): create_role_agent(role, FakeChatModel(), TOOL_REGISTRY)


def test_role_agent_handles_two_tool_rounds():
    role = RoleRegistry("src/studio/roles").get("strategist")
    model = FakeChatModel([
        AIMessage(content="", tool_calls=[{"name": "load_skill", "args": {"name": "brand-strategy"}, "id": "1"}]),
        AIMessage(content="", tool_calls=[{"name": "word_count", "args": {"text": "one two"}, "id": "2"}]),
        "answer",
    ])
    assert create_role_agent(role, model, TOOL_REGISTRY).invoke("task") == "answer"


def test_role_agent_stops_at_tool_call_limit():
    role = RoleRegistry("src/studio/roles").get("strategist")
    call = {"name": "word_count", "args": {"text": "one"}, "id": "1"}
    agent = create_role_agent(role, FakeChatModel([AIMessage(content="", tool_calls=[call])] * 8), TOOL_REGISTRY)
    assert "tool-call limit" in agent.invoke("task")


def test_load_skill_rejects_undeclared_skill():
    role = RoleRegistry("src/studio/roles").get("strategist")
    agent = create_role_agent(role, FakeChatModel(), TOOL_REGISTRY)
    tool = next(tool for tool in agent.tools if tool.name == "load_skill")
    with pytest.raises(ValueError):
        tool.invoke({"name": "copywriting"})
