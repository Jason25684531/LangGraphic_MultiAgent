from typing import Literal

from pydantic import BaseModel


class ReviewResult(BaseModel):
    status: Literal["pass", "revise"]
    feedback: str


def review(model, request: str, result: str) -> ReviewResult:
    prompt = f"""You are the Studio Review Director. Review the result against the original request for relevance, completeness, strategic coherence, cross-discipline consistency, clarity, unsupported assumptions, and execution readiness. Return pass only when it is ready; otherwise return revise with specific, actionable, scoped feedback.

Original request:
{request}

Result:
{result}"""
    for _ in range(2):
        try:
            return model.with_structured_output(ReviewResult).invoke(prompt)
        except Exception:
            pass
    return ReviewResult(status="revise", feedback="Review output was invalid; revise the result.")
