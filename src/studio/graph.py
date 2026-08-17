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
        task = state["request"]
        if state.get("result"):
            task += f"\nPrevious result: {state['result']}"
        if state.get("review_feedback"):
            task += f"\nPrevious review feedback: {state['review_feedback']}"
        result, delegations = supervisor.invoke(task, settings.max_agent_turns)
        return {"result": result, "iteration": state.get("iteration", 0) + 1, "delegations": delegations}

    def reviewer(state: StudioState):
        verdict = review(model, state["request"], state["result"])
        return {"review_status": verdict.status, "review_feedback": verdict.feedback}

    graph = StateGraph(StudioState)
    graph.add_node("studio", studio)
    graph.add_node("review", reviewer)
    graph.add_edge(START, "studio")
    graph.add_edge("studio", "review")
    graph.add_conditional_edges("review", lambda state: route_after_review(state, settings.max_iterations), {"studio": "studio", END: END})
    return graph.compile()
