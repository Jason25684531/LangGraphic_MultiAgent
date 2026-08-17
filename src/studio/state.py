from typing import TypedDict


class DelegationRecord(TypedDict, total=False):
    role: str
    task: str
    ok: bool
    error: str


class StudioState(TypedDict):
    request: str
    result: str
    review_status: str
    review_feedback: str
    iteration: int
    delegations: list[DelegationRecord]
