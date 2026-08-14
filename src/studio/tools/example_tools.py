from langchain_core.tools import tool


@tool
def get_magic_number() -> int:
    """Return the diagnostic magic number."""
    return 42


@tool
def word_count(text: str) -> int:
    """Count whitespace-separated words."""
    return len(text.split())
