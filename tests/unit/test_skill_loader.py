import pytest
from studio.skills.loader import SkillNotFoundError, load_skill


def test_skill_loading_is_safe():
    assert "audience" in load_skill("brand-strategy")
    with pytest.raises((ValueError, SkillNotFoundError)): load_skill("../secret")
    with pytest.raises(SkillNotFoundError): load_skill("missing")
