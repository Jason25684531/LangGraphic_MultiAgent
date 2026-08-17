from studio.config import StudioSettings
from studio.graph import create_studio_graph
from studio.roles.loader import RoleRegistry
from studio.testing import FakeChatModel
from studio.tools.registry import TOOL_REGISTRY
from langchain_core.messages import AIMessage


def test_offline_graph_passes():
    call = {"name": "delegate_task", "args": {"role": "strategist", "task": "brief"}, "id": "1"}
    graph = create_studio_graph(lambda _: FakeChatModel([AIMessage(content="", tool_calls=[call]), "draft", "synthesis", '{"status":"pass","feedback":"good"}']), TOOL_REGISTRY, RoleRegistry("src/studio/roles"), StudioSettings())
    state = graph.invoke({"request":"brief", "result":"", "review_status":"", "review_feedback":"", "iteration":0, "delegations":[]})
    assert state["review_status"] == "pass"
    assert state["delegations"][0]["role"] == "strategist"


def test_offline_graph_delegates_multiple_roles():
    calls = [
        {"name": "delegate_task", "args": {"role": "strategist", "task": "strategy"}, "id": "1"},
        {"name": "delegate_task", "args": {"role": "art_director", "task": "art"}, "id": "2"},
    ]
    graph = create_studio_graph(lambda _: FakeChatModel([AIMessage(content="", tool_calls=calls), "strategy", "art", "synthesis", '{"status":"pass","feedback":"good"}']), TOOL_REGISTRY, RoleRegistry("src/studio/roles"), StudioSettings())
    state = graph.invoke({"request":"brief", "result":"", "review_status":"", "review_feedback":"", "iteration":0, "delegations":[]})
    assert {entry["role"] for entry in state["delegations"]} == {"strategist", "art_director"}


def test_graph_delegates_a_new_registry_role_without_graph_changes(tmp_path):
    (tmp_path / "motion_designer.yaml").write_text(
        "name: motion_designer\ndescription: Develop motion direction\nsystem_prompt: Direct motion.\n"
    )
    call = {"name": "delegate_task", "args": {"role": "motion_designer", "task": "Develop motion direction"}, "id": "1"}
    graph = create_studio_graph(lambda _: FakeChatModel([AIMessage(content="", tool_calls=[call]), "motion plan", "synthesis", '{"status":"pass","feedback":"good"}']), TOOL_REGISTRY, RoleRegistry(tmp_path), StudioSettings())
    state = graph.invoke({"request":"Develop motion direction for a logo reveal.", "result":"", "review_status":"", "review_feedback":"", "iteration":0, "delegations":[]})
    assert state["delegations"] == [{"role": "motion_designer", "task": "Develop motion direction", "ok": True}]


def test_revision_feeds_request_result_and_feedback_to_supervisor():
    model = FakeChatModel(["draft one", '{"status":"revise","feedback":"make it bolder"}', "draft two", '{"status":"pass","feedback":"good"}'])
    graph = create_studio_graph(lambda _: model, TOOL_REGISTRY, RoleRegistry("src/studio/roles"), StudioSettings())
    state = graph.invoke({"request":"brief", "result":"", "review_status":"", "review_feedback":"", "iteration":0, "delegations":[]})
    assert state["iteration"] == 2
    second_supervisor_messages = model.prompts[2]
    assert "Previous result: draft one" in second_supervisor_messages[1].content
    assert "Previous review feedback: make it bolder" in second_supervisor_messages[1].content


def test_review_retry_exhaustion_ends_offline():
    model = FakeChatModel([
        "draft one", '{"status":"revise","feedback":"again"}',
        "draft two", '{"status":"revise","feedback":"again"}',
        "draft three", '{"status":"revise","feedback":"again"}',
    ])
    graph = create_studio_graph(lambda _: model, TOOL_REGISTRY, RoleRegistry("src/studio/roles"), StudioSettings(max_iterations=3))
    state = graph.invoke({"request":"brief", "result":"", "review_status":"", "review_feedback":"", "iteration":0, "delegations":[]})
    assert state["iteration"] == 3 and state["review_status"] == "revise"
