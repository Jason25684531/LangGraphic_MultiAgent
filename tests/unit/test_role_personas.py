from pathlib import Path

import yaml

from studio.roles.loader import RoleRegistry
from studio.skills.loader import load_skill_metadata
from studio.tools.registry import TOOL_REGISTRY


ROLES = Path("src/studio/roles")
SKILLS = Path("src/studio/skills")
EXPECTED_SKILLS = {
    "strategist": {"brand-strategy", "audience-definition"},
    "researcher": {"research-planning", "competitive-analysis", "reference-analysis"},
    "copywriter": {"copywriting", "messaging", "tone-of-voice"},
    "art_director": {"visual-direction", "typography", "image-prompting"},
    "designer": {"visual-direction", "typography", "layout-design"},
    "motion_designer": {"visual-direction", "motion-direction", "animation-timing"},
}


def test_role_personas_are_descriptive_and_complete():
    roles = list(RoleRegistry(ROLES))
    descriptions = [role.description for role in roles]
    assert len(descriptions) == len(set(descriptions))
    for role in roles:
        assert len(role.description) >= 40
        assert len(role.system_prompt) >= 300
        assert {"Identity:", "Primary responsibility:", "Thinking:", "Working principles:", "Expected outputs:", "Boundaries:", "Collaboration:"} <= set(
            line.split()[0] + (" " + line.split()[1] if len(line.split()) > 1 else "") for line in role.system_prompt.splitlines() if line
        ) or all(label in role.system_prompt for label in ("Identity:", "Primary responsibility:", "Thinking:", "Working principles:", "Expected outputs:", "Boundaries:", "Collaboration:"))
        assert set(role.skills) == EXPECTED_SKILLS[role.name]
        assert all((SKILLS / skill / "SKILL.md").is_file() for skill in role.skills)
        assert all(tool in TOOL_REGISTRY for tool in role.tools)


def test_skill_matrix_frontmatter_matches_directories():
    for role in RoleRegistry(ROLES):
        for skill in role.skills:
            assert load_skill_metadata(skill).name == skill


def test_skill_packs_have_the_required_structure():
    expected = set().union(*EXPECTED_SKILLS.values())
    assert {path.parent.name for path in SKILLS.glob("*/SKILL.md")} == expected
    for skill in expected:
        body = (SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")
        assert all(f"## {heading}" in body for heading in ("Use When", "Inputs", "Process", "Output", "Validation", "Avoid"))


def test_role_yaml_is_valid_configuration():
    for path in ROLES.glob("*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["name"] in EXPECTED_SKILLS
