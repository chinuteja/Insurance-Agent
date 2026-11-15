
from app.graph.claim_agent_state import ClaimAgentState


def set_current_agent(agent_name: str) -> dict:
    """Set the agent currently executing."""

    return {
        "current_agent": agent_name
    }


def record_agent_result(
    state: ClaimAgentState,
    agent_name: str,
    result: dict,
) -> dict:
    """
    Store a successful agent result and mark it completed.
    """

    agent_results = dict(
        state.get("agent_results") or {}
    )

    completed_agents = list(
        state.get("completed_agents") or []
    )

    agent_results[agent_name] = result

    if agent_name not in completed_agents:
        completed_agents.append(agent_name)

    return {
        "agent_results": agent_results,
        "completed_agents": completed_agents,
        "current_agent": None,
    }


def record_agent_error(
    state: ClaimAgentState,
    agent_name: str,
    error: str,
) -> dict:
    """
    Record an agent failure.

    Failed agents are not added to completed_agents.
    Human review is mandatory after an execution failure.
    """

    agent_errors = list(
        state.get("agent_errors") or []
    )

    agent_errors.append({
        "agent": agent_name,
        "error": error,
    })

    return {
        "agent_errors": agent_errors,
        "current_agent": None,
        "requires_human_review": True,
    }
