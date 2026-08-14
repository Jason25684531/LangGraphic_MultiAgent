import re
from pathlib import Path

ROOT = Path(__file__).parent
_NAME = re.compile(r"^[a-z0-9-]+$")


class SkillNotFoundError(ValueError):
    pass


def load_skill(name: str, root: str | Path = ROOT) -> str:
    if not _NAME.fullmatch(name):
        raise ValueError(f"Invalid skill name: {name}")
    root_path = Path(root).resolve()
    target = (root_path / name / "SKILL.md").resolve()
    if root_path not in target.parents or not target.is_file():
        raise SkillNotFoundError(f"Skill not found: {name}")
    return target.read_text(encoding="utf-8")
