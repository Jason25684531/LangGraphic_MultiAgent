from langgraph.graph import END, START, StateGraph

from studio.agents.reviewer import review
from studio.agents.supervisor import Supervisor
from studio.skills.loader import load_skill
from studio.state import StudioState


def route_after_review(state: StudioState, max_iterations: int):
    if state["review_status"] == "pass" or state["iteration"] >= max_iterations:
        return END
    return "studio"


def create_studio_graph(model_factory, tool_registry, role_registry, settings):
    model = model_factory(settings)
    supervisor = Supervisor(role_registry, model, tool_registry, load_skill)

    def studio(state: StudioState):
        roles = ["strategist"] if "strategist" in role_registry.roles else [next(iter(role_registry)).name]
        if "multi" in state["request"].lower():
            roles = [role for role in ("strategist", "art_director") if role in role_registry.roles]
        task = state["request"]
        if state.get("review_feedback"):
            task += f"\nPrevious review feedback: {state['review_feedback']}"
        results = [supervisor.delegate_task(role, task) for role in roles]
        return {"result": "\n".join(results), "iteration": state.get("iteration", 0) + 1,
                "delegations": supervisor.delegations.copy()}

    def reviewer(state: StudioState):
        verdict = review(model, state["result"])
        return {"review_status": verdict.status, "review_feedback": verdict.feedback}

    graph = StateGraph(StudioState)
    graph.add_node("studio", studio)
    graph.add_node("review", reviewer)
    graph.add_edge(START, "studio")
    graph.add_edge("studio", "review")
    graph.add_conditional_edges("review", lambda state: route_after_review(state, settings.max_iterations), {"studio": "studio", END: END})
    return graph.compile()
