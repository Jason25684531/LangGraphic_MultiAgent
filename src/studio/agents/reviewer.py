from typing import Literal

from pydantic import BaseModel


class ReviewResult(BaseModel):
    status: Literal["pass", "revise"]
    feedback: str


def review(model, result: str) -> ReviewResult:
    prompt = f"Review this result. Return pass or revise with feedback.\n{result}"
    for _ in range(2):
        try:
            return model.with_structured_output(ReviewResult).invoke(prompt)
        except Exception:
            pass
    return ReviewResult(status="revise", feedback="Review output was invalid; revise the result.")
