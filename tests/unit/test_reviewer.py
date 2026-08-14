from studio.agents.reviewer import review
from studio.testing import FakeChatModel


def test_reviewer_pass_and_malformed_fallback():
    assert review(FakeChatModel(['{"status":"pass","feedback":"ok"}']), "draft").status == "pass"
    assert review(FakeChatModel(["bad", "bad"]), "draft").status == "revise"
