import re
from pathlib import Path

import yaml
from pydantic import BaseModel

ROOT = Path(__file__).parent
_NAME = re.compile(r"^[a-z0-9-]+$")


class SkillNotFoundError(ValueError):
    pass


class SkillMetadata(BaseModel):
    name: str
    description: str = ""


def load_skill(name: str, root: str | Path = ROOT) -> str:
    if not _NAME.fullmatch(name):
        raise ValueError(f"Invalid skill name: {name}")
    root_path = Path(root).resolve()
    target = (root_path / name / "SKILL.md").resolve()
    if root_path not in target.parents or not target.is_file():
        raise SkillNotFoundError(f"Skill not found: {name}")
    return target.read_text(encoding="utf-8")


def load_skill_metadata(name: str, root: str | Path = ROOT) -> SkillMetadata:
    content = load_skill(name, root)
    if not content.startswith("---\n"):
        return SkillMetadata(name=name)
    _, _, rest = content.partition("---\n")
    frontmatter, marker, _ = rest.partition("---\n")
    if not marker:
        return SkillMetadata(name=name)
    data = yaml.safe_load(frontmatter) or {}
    return SkillMetadata(name=data.get("name", name), description=data.get("description", ""))
