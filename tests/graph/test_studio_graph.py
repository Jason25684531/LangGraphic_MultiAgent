from studio.config import StudioSettings
from studio.graph import create_studio_graph
from studio.roles.loader import RoleRegistry
from studio.testing import FakeChatModel
from studio.tools.registry import TOOL_REGISTRY


def test_offline_graph_passes():
    graph = create_studio_graph(lambda _: FakeChatModel(["draft", '{"status":"pass","feedback":"good"}']), TOOL_REGISTRY, RoleRegistry("src/studio/roles"), StudioSettings())
    state = graph.invoke({"request":"brief", "result":"", "review_status":"", "review_feedback":"", "iteration":0, "delegations":[]})
    assert state["review_status"] == "pass"
    assert state["delegations"][0]["role"] == "strategist"


def test_offline_graph_delegates_multiple_roles():
    graph = create_studio_graph(lambda _: FakeChatModel(["strategy", "art", '{"status":"pass","feedback":"good"}']), TOOL_REGISTRY, RoleRegistry("src/studio/roles"), StudioSettings())
    state = graph.invoke({"request":"multi discipline brief", "result":"", "review_status":"", "review_feedback":"", "iteration":0, "delegations":[]})
    assert {entry["role"] for entry in state["delegations"]} == {"strategist", "art_director"}
