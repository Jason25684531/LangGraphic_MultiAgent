from studio.agents.reviewer import review
from studio.testing import FakeChatModel


def test_reviewer_pass_and_malformed_fallback():
    model = FakeChatModel(['{"status":"pass","feedback":"ok"}'])
    assert review(model, "REQUEST_TOKEN", "RESULT_TOKEN").status == "pass"
    assert "REQUEST_TOKEN" in model.prompts[0] and "RESULT_TOKEN" in model.prompts[0]
    assert review(FakeChatModel(["bad", "bad"]), "request", "draft").status == "revise"
