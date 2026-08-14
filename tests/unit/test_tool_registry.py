import pytest
from studio.tools.registry import UnknownToolError, resolve_tools


def test_tool_registry():
    assert [tool.name for tool in resolve_tools(["get_magic_number"])] == ["get_magic_number"]
    with pytest.raises(UnknownToolError): resolve_tools(["missing"])
