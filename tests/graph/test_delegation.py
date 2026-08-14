from studio.agents.supervisor import Supervisor
from studio.roles.loader import RoleRegistry
from studio.skills.loader import load_skill
from studio.testing import FakeChatModel
from studio.tools.registry import TOOL_REGISTRY


def test_delegation_and_unknown_role():
    supervisor = Supervisor(RoleRegistry("src/studio/roles"), FakeChatModel(["answer"]), TOOL_REGISTRY, load_skill)
    assert supervisor.delegate_task("strategist", "task") == "answer"
    assert "Unknown role" in supervisor.delegate_task("nope", "task")
    assert len(supervisor.model.prompts) == 1
