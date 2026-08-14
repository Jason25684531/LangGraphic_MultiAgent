from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class RoleConfig(BaseModel):
    name: str
    description: str
    system_prompt: str
    skills: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    model_profile: str = "default"


class UnknownRoleError(KeyError):
    pass


def load_role(path: str | Path) -> RoleConfig:
    with Path(path).open(encoding="utf-8") as handle:
        return RoleConfig.model_validate(yaml.safe_load(handle))


class RoleRegistry:
    def __init__(self, roles_dir: str | Path):
        self.roles = {role.name: role for role in (load_role(path) for path in Path(roles_dir).glob("*.yaml"))}

    def get(self, name: str) -> RoleConfig:
        try:
            return self.roles[name]
        except KeyError as exc:
            raise UnknownRoleError(f"Unknown role: {name}") from exc

    def __iter__(self):
        return iter(self.roles.values())
