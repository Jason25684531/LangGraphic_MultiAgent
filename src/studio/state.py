from typing import TypedDict


class StudioState(TypedDict):
    request: str
    result: str
    review_status: str
    review_feedback: str
    iteration: int
    delegations: list[dict]
