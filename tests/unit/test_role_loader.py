import pytest
from pydantic import ValidationError

from studio.roles.loader import RoleConfig, RoleRegistry, UnknownRoleError, load_role


def test_load_roles():
    registry = RoleRegistry("src/studio/roles")
    assert registry.get("strategist").name == "strategist"
    with pytest.raises(UnknownRoleError): registry.get("missing")


def test_invalid_role(tmp_path):
    path = tmp_path / "bad.yaml"; path.write_text("name: bad")
    with pytest.raises(ValidationError): load_role(path)
