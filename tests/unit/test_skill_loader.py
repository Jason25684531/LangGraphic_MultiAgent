import pytest
from studio.skills.loader import SkillNotFoundError, load_skill, load_skill_metadata


def test_skill_loading_is_safe():
    assert "audience" in load_skill("brand-strategy")
    with pytest.raises((ValueError, SkillNotFoundError)): load_skill("../secret")
    with pytest.raises(SkillNotFoundError): load_skill("missing")


def test_skill_metadata_is_safe_and_tolerates_legacy_skills(tmp_path):
    (tmp_path / "known").mkdir()
    (tmp_path / "known" / "SKILL.md").write_text("---\nname: known\ndescription: Useful\n---\nbody")
    assert load_skill_metadata("known", tmp_path).description == "Useful"
    with pytest.raises((ValueError, SkillNotFoundError)):
        load_skill_metadata("../secret", tmp_path)
