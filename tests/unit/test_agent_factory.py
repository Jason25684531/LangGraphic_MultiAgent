import pytest
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
    assert {tool.name for tool in agent.tools} == {"word_count", "load_skill"}


def test_unknown_tool_fails():
    role = RoleRegistry("src/studio/roles").get("strategist").model_copy(update={"tools": ["nope"]})
    with pytest.raises(KeyError): create_role_agent(role, FakeChatModel(), TOOL_REGISTRY)
