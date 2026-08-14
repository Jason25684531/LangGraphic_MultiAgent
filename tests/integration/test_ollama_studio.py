import pytest
from studio.config import StudioSettings
from studio.graph import create_studio_graph
from studio.models.factory import create_chat_model
from studio.roles.loader import RoleRegistry
from studio.tools.registry import TOOL_REGISTRY

pytestmark = pytest.mark.ollama


def test_studio_e2e(ollama_settings):
    graph = create_studio_graph(create_chat_model, TOOL_REGISTRY, RoleRegistry("src/studio/roles"), StudioSettings())
    state = graph.invoke({"request":"Create a brand brief.", "result":"", "review_status":"", "review_feedback":"", "iteration":0, "delegations":[]})
    assert state["result"] and state["delegations"]
    assert {entry["role"] for entry in state["delegations"]} == {"strategist"}
