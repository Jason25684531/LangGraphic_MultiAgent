import sys

from studio.config import StudioSettings
from studio.graph import create_studio_graph
from studio.models.factory import create_chat_model
from studio.roles.loader import RoleRegistry
from studio.tools.registry import TOOL_REGISTRY


def main():
    request = " ".join(sys.argv[1:]) or "Create a concise design brief."
    root = __import__("pathlib").Path(__file__).parent
    graph = create_studio_graph(create_chat_model, TOOL_REGISTRY, RoleRegistry(root / "roles"), StudioSettings())
    state = graph.invoke({"request": request, "result": "", "review_status": "", "review_feedback": "", "iteration": 0, "delegations": []})
    print("Delegations:", state["delegations"])
    print("Result:", state["result"])


if __name__ == "__main__":
    main()
