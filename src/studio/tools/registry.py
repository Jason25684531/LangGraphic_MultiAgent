from .example_tools import get_magic_number, word_count

TOOL_REGISTRY = {tool.name: tool for tool in (get_magic_number, word_count)}


class UnknownToolError(KeyError):
    pass


def resolve_tools(names: list[str], registry=TOOL_REGISTRY):
    missing = [name for name in names if name not in registry]
    if missing:
        raise UnknownToolError(f"Unknown tool: {missing[0]}")
    return [registry[name] for name in names]
