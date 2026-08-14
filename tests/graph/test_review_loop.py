from langgraph.graph import END
from studio.graph import route_after_review


def test_routes():
    assert route_after_review({"review_status": "pass", "iteration": 1}, 3) == END
    assert route_after_review({"review_status": "revise", "iteration": 1}, 3) == "studio"
    assert route_after_review({"review_status": "revise", "iteration": 3}, 3) == END
