from pathlib import Path

from langchain_core.messages import AIMessage

from studio.agents.supervisor import DelegationResult, Supervisor
from studio.roles.loader import RoleRegistry
from studio.skills.loader import load_skill
from studio.testing import FakeChatModel
from studio.tools.registry import TOOL_REGISTRY


def test_delegation_and_unknown_role():
    supervisor = Supervisor(RoleRegistry("src/studio/roles"), FakeChatModel(["answer"]), TOOL_REGISTRY, load_skill)
    assert supervisor.delegate_task("strategist", "task").result == "answer"
    assert not supervisor.delegate_task("nope", "task").ok
    assert len(supervisor.model.prompts) == 1


def test_delegation_result_is_json_safe_and_failures_do_not_raise():
    result = DelegationResult(role="nope", task="task", ok=False, error="Unknown role: nope")
    assert result.model_dump_json()


def test_supervisor_runs_llm_tool_loop_and_only_binds_delegate_task():
    model = FakeChatModel([
        AIMessage(content="", tool_calls=[{"name": "delegate_task", "args": {"role": "strategist", "task": "plan"}, "id": "call-1"}]),
        "specialist result",
        "supervisor synthesis",
    ])
    supervisor = Supervisor(RoleRegistry("src/studio/roles"), model, TOOL_REGISTRY, load_skill)
    result, delegations = supervisor.invoke("brief")
    assert result == "supervisor synthesis"
    assert delegations == [{"role": "strategist", "task": "plan", "ok": True}]
    assert {tool.name for tool in model.bound_tools[0]} == {"delegate_task"}


def test_supervisor_discovers_dynamic_roles_without_graph_role_names(tmp_path):
    (tmp_path / "motion_designer.yaml").write_text(
        "name: motion_designer\ndescription: Develop motion direction\nsystem_prompt: Direct motion.\n"
    )
    supervisor = Supervisor(RoleRegistry(tmp_path), FakeChatModel(), TOOL_REGISTRY, load_skill)
    assert "motion_designer: Develop motion direction" in supervisor.prompt
    graph_source = Path("src/studio/graph.py").read_text(encoding="utf-8")
    assert "strategist" not in graph_source and "art_director" not in graph_source


def test_supervisor_includes_dynamic_ux_designer_description(tmp_path):
    (tmp_path / "ux_designer.yaml").write_text(
        "name: ux_designer\ndescription: Design user flows and information architecture.\nsystem_prompt: Coordinate UX work.\n"
    )
    supervisor = Supervisor(RoleRegistry(tmp_path), FakeChatModel(), TOOL_REGISTRY, load_skill)
    assert "ux_designer: Design user flows and information architecture." in supervisor.prompt
